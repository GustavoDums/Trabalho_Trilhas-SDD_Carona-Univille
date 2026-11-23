"""Reproduz a T045 pela interface HTTP da PoC local com contas fictícias."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from getpass import getpass
from http.cookiejar import CookieJar
import re
from secrets import token_urlsafe
from threading import Barrier
from time import perf_counter
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPCookieProcessor, Request, build_opener
from zoneinfo import ZoneInfo


DRIVER = ("mariana.motorista@univille.br", "Mariana Sintética")
PASSENGERS = (
    ("joao.silva@univille.br", "João Sintético"),
    ("lucas.aluno@univille.br", "Lucas Sintético"),
)
POINTS = ("Terminal Central", "Terminal Norte", "Bairro América", "Campus Univille")
PANEL = "/caronas/minhas-reservas/"
SEARCH = "/caronas/buscar/"


def expect(condition, message):
    if not condition:
        raise RuntimeError(message)


class Session:
    def __init__(self, port):
        self.base = f"http://127.0.0.1:{port}"
        self.cookies = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cookies))

    def request(self, path, fields=None):
        url = self.base + path
        if fields is None:
            request = Request(url)
        else:
            token = next((cookie.value for cookie in self.cookies if cookie.name == "csrftoken"), None)
            expect(token, "Sessão sem token CSRF. Abra o formulário antes do envio.")
            data = urlencode(dict(fields, csrfmiddlewaretoken=token)).encode()
            request = Request(url, data=data, headers={"Referer": url})
        with self.opener.open(request, timeout=15) as response:
            return urlsplit(response.url).path, response.read().decode("utf-8")

    def login(self, email, password):
        self.request("/accounts/login/")
        return self.request("/accounts/login/", {"email": email, "password": password})

    def register_and_activate(self, person, password, role):
        email, name = person
        self.request("/accounts/register/")
        path, _ = self.request("/accounts/register/", {
            "email": email, "full_name": name, "role": role,
            "password": password, "password_confirm": password,
        })
        expect(path == "/accounts/login/", "O cadastro deve levar ao login manual. Use uma base nova.")
        path, html = self.login(email, password)
        expect(path == "/accounts/activation/" and "Pendente" in html, "O vínculo deveria iniciar pendente.")
        path, html = self.request("/accounts/activation/", {})
        expect(path == "/accounts/profile/" and "Ativo" in html, "A ativação deveria liberar o perfil.")


def find_id(html, pattern, message):
    match = re.search(pattern, html)
    expect(match is not None, message)
    return int(match.group(1))


def points_from(html):
    return tuple(find_id(html, rf'<option value="(\d+)"[^>]*>{re.escape(name)}</option>',
                         f"Ponto ausente no catálogo web: {name}.") for name in POINTS)


def contest(sessions, offer_id, boarding, alighting):
    ready = Barrier(2, timeout=10)

    def reserve(session):
        ready.wait()
        return session.request(f"/caronas/{offer_id}/reservar/", {
            "boarding_point_id": boarding, "alighting_point_id": alighting,
        })

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(reserve, sessions, timeout=25))
    winners = [i for i, (path, html) in enumerate(responses)
               if path == PANEL and "Reserva confirmada com sucesso." in html]
    refusals = [html for _, html in responses if "Não há vagas disponíveis para esta carona." in html]
    expect(len(winners) == len(refusals) == 1, "A disputa deve produzir uma confirmação e uma recusa por esgotamento.")
    return winners[0]


def rehearse(port):
    start = checkpoint = perf_counter()

    def record(message):
        nonlocal checkpoint
        now = perf_counter()
        print(f"{now - checkpoint:6.2f} s  {message}", flush=True)
        checkpoint = now

    password = "Demo!" + token_urlsafe(16)
    driver = Session(port)
    passengers = (Session(port), Session(port))
    driver.register_and_activate(DRIVER, password, "MOTORISTA")
    for passenger, person in zip(passengers, PASSENGERS):
        passenger.register_and_activate(person, password, "PASSAGEIRO")
    record("Cadastro, login e ativação de três contas fictícias.")

    origin, stop, second_stop, destination = points_from(driver.request("/caronas/oferecer/")[1])
    departure = datetime.now(ZoneInfo("America/Sao_Paulo")) + timedelta(days=1)
    local = departure.strftime("%Y-%m-%dT%H:%M")
    path, html = driver.request("/caronas/oferecer/", {
        "origin": origin, "destination": destination, "departure_at": local,
        "seats": 1, "vehicle_model": "Veículo Demo", "vehicle_color": "Azul", "vehicle_plate": "FICTUC1",
        "waypoints-TOTAL_FORMS": 2, "waypoints-INITIAL_FORMS": 0,
        "waypoints-0-point": stop, "waypoints-1-point": second_stop,
    })
    expect(path == "/caronas/minhas-ofertas/", "A publicação deve abrir Minhas ofertas.")
    indices = [html.find(name) for name in POINTS]
    expect(min(indices) >= 0 and indices == sorted(indices), "A oferta deve preservar a ordem das duas paradas.")
    offer_id = find_id(html, r'data-offer-id="(\d+)"', "Oferta ausente no painel do motorista.")
    record(f"Oferta {offer_id} publicada com duas paradas ordenadas e uma vaga.")

    search = SEARCH + "?" + urlencode({"boarding_id": stop, "alighting_id": destination, "desired_at": local})
    for passenger in passengers:
        _, html = passenger.request(search)
        expect(f'data-offer-id="{offer_id}"' in html and "1 vaga disponível" in html, "A busca deve encontrar a vaga.")
    record("Busca por trecho intermediário e horário encontrou uma vaga.")

    winner = contest(passengers, offer_id, stop, destination)
    _, html = passengers[1 - winner].request(search)
    expect("Vagas esgotadas." in html, "A busca deve informar esgotamento após a disputa.")
    _, html = passengers[winner].request(PANEL)
    booking_id = find_id(html, r'data-booking-id="(\d+)"', "Reserva ausente no painel do titular.")
    expect("Estado: CONFIRMADA" in html, "O vencedor deve ter uma reserva confirmada.")
    record(f"Dois POSTs concorrentes: passageiro {winner + 1} confirmado, outro recusado. Saldo zero.")

    path, html = passengers[winner].request(f"/caronas/reservas/{booking_id}/cancelar/", {})
    expect(path == PANEL and "Estado: CANCELADA" in html, "O histórico deve preservar a reserva cancelada.")
    _, html = passengers[1 - winner].request(search)
    expect("1 vaga disponível" in html, "O cancelamento deve devolver a vaga à busca.")
    record("Cancelamento pelo titular manteve o histórico e liberou a vaga.")
    elapsed = perf_counter() - start
    expect(elapsed < 600, "O ensaio técnico excedeu 10 minutos.")
    print(f"Total cronometrado do fluxo web: {elapsed:.2f} s.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--porta", type=int, default=8000)
    parser.add_argument("--disputar", type=int, metavar="OFERTA", help="Disputa uma oferta preparada no navegador.")
    args = parser.parse_args()
    if args.disputar is None:
        rehearse(args.porta)
        return
    sessions = (Session(args.porta), Session(args.porta))
    password = getpass("Senha fictícia comum dos dois passageiros: ")
    for session, (email, _) in zip(sessions, PASSENGERS):
        path, _ = session.login(email, password)
        expect(path == "/accounts/profile/", "Prepare as duas contas fictícias ativas antes da disputa.")
    _, stop, _, destination = points_from(sessions[0].request(SEARCH)[1])
    winner = contest(sessions, args.disputar, stop, destination)
    print(f"Passageiro {winner + 1}: confirmado. Outro passageiro: vaga esgotada.")


if __name__ == "__main__":
    main()
