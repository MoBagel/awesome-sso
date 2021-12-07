from awesome_sso.exceptions import BadRequest, Unauthorized, NotFound, ResourceGone, UnprocessableEntity, InternalServerError


def test_exception_format():
    assert BadRequest("msg").status_code == 400
    assert Unauthorized("msg").status_code == 401
    assert NotFound("msg").status_code == 403
    assert ResourceGone("msg").status_code == 410
    assert UnprocessableEntity("msg").status_code == 422
    assert InternalServerError("msg").status_code == 500
