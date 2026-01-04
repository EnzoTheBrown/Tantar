import json
import os
import sys
import time
import uuid
from pathlib import Path
from urllib import request, parse, error


API_URL = os.getenv("API_URL", "http://api:8000").rstrip("/")
TIMEOUT = int(os.getenv("CLIENT_TIMEOUT_SECONDS", "5"))
RETRIES = int(os.getenv("RETRIES", "30"))
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "2"))
ALLOW_FILE_FAILURE = os.getenv("ALLOW_FILE_FAILURE", "0") == "1"
ALLOW_EVENT_FAILURE = os.getenv("ALLOW_EVENT_FAILURE", "0") == "1"
ALLOW_EVENTS_FAILURE = os.getenv("ALLOW_EVENTS_FAILURE", "0") == "1"
ALLOW_COMPANY_DELETE_FAILURE = os.getenv("ALLOW_COMPANY_DELETE_FAILURE", "0") == "1"
LOG_FILE = os.getenv("LOG_FILE")


def log(message):
    print(message)
    if LOG_FILE:
        with open(LOG_FILE, "a", encoding="utf-8") as handle:
            handle.write(f"{message}\n")


def wait_for_api():
    health_url = f"{API_URL}/health"
    log(f"Waiting for API at {health_url}")
    for _ in range(RETRIES):
        try:
            req = request.Request(health_url, method="GET")
            with request.urlopen(req, timeout=TIMEOUT) as resp:
                if resp.status == 200:
                    log("API is healthy")
                    return
        except Exception:
            time.sleep(SLEEP_SECONDS)
    raise RuntimeError("API did not become healthy in time")


def read_response(resp):
    body = resp.read()
    content_type = resp.headers.get("Content-Type", "")
    if not body:
        return None
    if "application/json" in content_type:
        return json.loads(body.decode("utf-8"))
    return body


def http_request(method, path, headers=None, data=None, expected=None):
    url = f"{API_URL}{path}"
    headers = headers or {}
    body = None
    if data is not None:
        if isinstance(data, (dict, list)):
            body = json.dumps(data).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        else:
            body = data
    req = request.Request(url, method=method, headers=headers, data=body)
    try:
        with request.urlopen(req, timeout=TIMEOUT) as resp:
            payload = read_response(resp)
            if expected and resp.status not in expected:
                raise RuntimeError(f"{method} {path} -> {resp.status}: {payload}")
            return resp.status, payload
    except error.HTTPError as exc:
        payload = exc.read()
        try:
            payload = json.loads(payload.decode("utf-8"))
        except Exception:
            payload = payload.decode("utf-8", errors="ignore")
        if expected and exc.code in expected:
            return exc.code, payload
        raise RuntimeError(f"{method} {path} -> {exc.code}: {payload}") from exc


def form_request(path, form, expected):
    data = parse.urlencode(form).encode("utf-8")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return http_request("POST", path, headers=headers, data=data, expected=expected)


def multipart_file_request(path, field_name, file_path, filename, content_type, query=None, token=None):
    boundary = uuid.uuid4().hex
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    lines = []
    lines.append(f"--{boundary}")
    lines.append(
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'
    )
    lines.append(f"Content-Type: {content_type}")
    lines.append("")
    body = "\r\n".join(lines).encode("utf-8") + b"\r\n" + file_bytes + b"\r\n"
    body += f"--{boundary}--\r\n".encode("utf-8")

    if query:
        query_string = parse.urlencode(query)
        path = f"{path}?{query_string}"
    return http_request("POST", path, headers=headers, data=body, expected=(201,))


def main():
    wait_for_api()

    user_email = f"client_{int(time.time())}@example.com"
    password = "Test1234!"

    log("POST /user")
    _, user = http_request(
        "POST",
        "/user",
        data={"email": user_email, "password": password, "invitation_token": None},
        expected=(201,),
    )

    log("POST /login")
    _, login_payload = form_request(
        "/login",
        {"username": user_email, "password": password},
        expected=(201,),
    )
    token = login_payload["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    log("GET /user")
    _, current_user = http_request("GET", "/user", headers=auth_headers, expected=(200,))
    account_id = current_user["account"]["original_id"]

    log("GET /users")
    http_request("GET", "/users", headers=auth_headers, expected=(200,))

    log("POST /account")
    _, created_account = http_request(
        "POST",
        "/account",
        headers=auth_headers,
        data={"name": "Client Test Account"},
        expected=(201,),
    )

    log("GET /account/{account_id}")
    http_request(
        "GET",
        f"/account/{created_account['original_id']}",
        headers=auth_headers,
        expected=(200,),
    )

    log("POST /company")
    _, company = http_request(
        "POST",
        "/company",
        headers=auth_headers,
        data={"name": "Client Test Company", "siren": "807385026"},
        expected=(201,),
    )
    company_id = company["original_id"]

    log("GET /company/{company_id}")
    http_request(
        "GET",
        f"/company/{company_id}",
        headers=auth_headers,
        expected=(200,),
    )

    log("GET /companies")
    http_request("GET", "/companies", headers=auth_headers, expected=(200,))

    log("PUT /company/{company_id}")
    http_request(
        "PUT",
        f"/company/{company_id}",
        headers=auth_headers,
        data={"name": "Client Test Company Updated", "siren": "807385026"},
        expected=(200,),
    )

    file_id = None
    log("POST /file")
    try:
        sample_pdf = Path("/app/fixtures/sample.pdf")
        _, file_payload = multipart_file_request(
            "/file",
            field_name="file",
            file_path=sample_pdf,
            filename="sample.pdf",
            content_type="application/pdf",
            query={"company_id": company_id},
            token=token,
        )
        file_id = file_payload["original_id"]
    except Exception as exc:
        if ALLOW_FILE_FAILURE:
            log(f"File upload skipped due to error: {exc}")
        else:
            raise

    log("GET /files")
    http_request("GET", "/files", headers=auth_headers, expected=(200,))

    if file_id:
        log("GET /file/{file_id}")
        http_request(
            "GET",
            f"/file/{file_id}",
            headers=auth_headers,
            expected=(200,),
        )

        log("GET /file/{file_id}/download")
        http_request(
            "GET",
            f"/file/{file_id}/download",
            headers=auth_headers,
            expected=(200,),
        )

        log("PATCH /company/{company_id}/file/{file_id}")
        http_request(
            "PATCH",
            f"/company/{company_id}/file/{file_id}",
            data={"title": "Invalid", "company_name": "Invalid", "siren": "000000000"},
            expected=(202,),
        )

        log("POST /company/{company_id}/event")
        event_expected = (201, 500) if ALLOW_EVENT_FAILURE else (201,)
        status, payload = http_request(
            "POST",
            f"/company/{company_id}/event",
            data={
                "original_id": str(uuid.uuid4()),
                "account_id": account_id,
                "company_id": company_id,
                "file_id": file_id,
                "date": "2024-01-01",
                "label": "Autorisations diverses",
                "type": "Autorisation de souscription à un prêt bancaire",
                "text": "Test event text",
                "title": "Test event",
                "page_index": 1,
                "file_name": "sample.pdf",
                "siren": "807385026",
            },
            expected=event_expected,
        )
        if status != 201:
            log(f"Event creation returned {status}: {payload}")

    log("GET /events")
    events_expected = (200, 500) if ALLOW_EVENTS_FAILURE else (200,)
    status, payload = http_request(
        "GET", "/events", headers=auth_headers, expected=events_expected
    )
    if status != 200:
        log(f"Events fetch returned {status}: {payload}")

    log("GET /categories")
    http_request("GET", "/categories", expected=(200,))

    log("GET /events/{id}/authorized_contracts (expected 404)")
    http_request(
        "GET",
        f"/events/{uuid.uuid4()}/authorized_contracts",
        headers=auth_headers,
        expected=(404,),
    )

    log("POST /ws/notify/{company_id}")
    http_request(
        "POST",
        f"/ws/notify/{company_id}",
        data={"type": "client_test"},
        expected=(200,),
    )

    log("DELETE /company/{company_id}")
    delete_expected = (204, 500) if ALLOW_COMPANY_DELETE_FAILURE else (204,)
    status, payload = http_request(
        "DELETE",
        f"/company/{company_id}",
        headers=auth_headers,
        expected=delete_expected,
    )
    if status != 204:
        log(f"Company delete returned {status}: {payload}")

    log("DELETE /user/{id}")
    http_request(
        "DELETE",
        f"/user/{current_user['original_id']}",
        expected=(204,),
    )

    log("Client scenario completed successfully.")


if __name__ == "__main__":
    main()
