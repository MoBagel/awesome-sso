from pydantic import EmailStr

from awesome_sso.mail.mailgun import MailGun


def test_send_message(mailgun: MailGun):
    resp = mailgun.send_simple_message(
        from_name="test",
        from_email=EmailStr("test@8ndpoint.com"),
        to=[EmailStr("schwannden@mobagel.com")],
        subject="test title",
        text="test content",
    )
    resp.close()


def test_send_template(mailgun: MailGun):
    resp = mailgun.send_template(
        from_name="test",
        from_email=EmailStr("test@8ndpoint.com"),
        to=[EmailStr("schwannden@mobagel.com")],
        subject="test title",
        template="test.alert",
        data={
            "title": "hello from unit test",
            "content": "test content from unit test",
        },
    )
    resp.close()
