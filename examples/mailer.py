"""
For each entered email, compose an email with a templated message.
"""

from markten import Recipe, actions, parameters

email_template = """
Hello [Enter student's name]!

Find your assignment results & feedback below:

* Overall mark: [Enter student's mark]%

Feedback:

[Replace this with your feedback]
""".strip()


mailer = Recipe("Email assignment results")


mailer.parameter("email", parameters.stdin("email"))


@mailer.step
def mail_student(action, email):
    return actions.email.compose(
        action,
        email,
        subject="Your assignment results",
        body=email_template,
    )


if __name__ == '__main__':
    mailer.run()
