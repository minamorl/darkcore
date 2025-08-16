from darkcore.reader import Reader
from darkcore.writer import Writer
from darkcore.state import State
from darkcore.result import Ok, Err

def test_reader_writer_state_result_integration():
    # Step1: read user from env
    get_user = Reader(lambda env: env.get("user"))

    # Step2: wrap into Result (fail if missing)
    def to_result(user):
        if user is None:
            return Err("no user")
        return Ok(user)

    # Step3: log the user using Writer
    def log_user(user):
        return Writer(user, [f"got user={user}"])

    # Step4: update state counter with State
    def update_state(user):
        return State(lambda s: (f"{user}@{s}", s+1))

    env = {"user": "alice"}

    # run integration
    user = get_user.run(env)
    result = to_result(user) >> (lambda u: Ok(log_user(u)))
    assert isinstance(result, Ok)

    writer: Writer = result.value
    assert writer.log == ["got user=alice"]

    # state part
    state_prog = update_state(writer.value)
    out, s2 = state_prog.run(42)
    assert out == "alice@42"
    assert s2 == 43
