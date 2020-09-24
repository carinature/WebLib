from flask_wtf import FlaskForm, RecaptchaField
import email_validator
# from wtforms import *
# from wtforms.validators import *

from wtforms import (StringField,
                     TextAreaField,
                     SubmitField,
                     PasswordField,
                     DateField,
                     SelectField, validators)
from wtforms.validators import (DataRequired,
    # Note there is a distinction between this and DataRequired in that
    # InputRequired looks that form-input data was provided, and DataRequired looks at the post-coercion data.
                                Email,
                                EqualTo,
                                Length,
                                URL, Optional)

EMPTY_LABEL = ''


class SearchSubject(FlaskForm):
    subject_keyword_1 = StringField(
        EMPTY_LABEL,
        [DataRequired(message='Did you forget to insert a search keyword'),
         validators.Regexp('^\w+$', message="Field accepts one search word")],
        render_kw={'placeholder': 'Subject'})
    subject_keyword_2 = StringField(
        EMPTY_LABEL,
        [Optional(), validators.Regexp('^\w+$', message="Field accepts one search word")],
        render_kw={'placeholder': '(Optional) Subject'})
    submit_subject = SubmitField('Submit')


class SearchReference(FlaskForm):

    def any_fields_filled(self):
        return any([self.search_author.data, self.search_work.data, self.search_reference.data])

    def validate(self):
        return self.any_fields_filled()

    search_author = StringField(
        'Author\'s name',
        [Optional()],  # , validators.Regexp('^\w+$', message="Field accepts one search word")],
        render_kw={'placeholder': 'Author\'s name'})
    search_work = StringField(
        'Work',
        [Optional()],  # , validators.Regexp('^\w+$', message="Field accepts one search word")],
        render_kw={'placeholder': 'Work'})
    search_reference = StringField(
        'Reference',
        [Optional()],  # , validators.Regexp('^\w+$', message="Field accepts one search word")],
        render_kw={'placeholder': 'Reference'})
    submit_reference = SubmitField('Submit')  # todo check that at least one field wasn't empty


class SignupForm(FlaskForm):
    """Sign up for a user account."""
    # email = StringField('Email', [
    #     Email(message='Not a valid email address.'),
    #     DataRequired()])
    password = PasswordField('Password', [
        DataRequired(message="Please enter a password."),
    ])
    confirmPassword = PasswordField('Repeat Password', [
        EqualTo(password, message='Passwords must match.')
    ])
    title = SelectField('Title', [DataRequired()],
                        choices=[('Farmer', 'farmer'),
                                 ('Corrupt Politician', 'politician'),
                                 ('No-nonsense City Cop', 'cop'),
                                 ('Professional Rocket League Player', 'rocket'),
                                 ('Lonely Guy At A Diner', 'lonely'),
                                 ('Pokemon Trainer', 'pokemon')])
    website = StringField('Website', validators=[URL()])
    birthday = DateField('Your Birthday')
    recaptcha = RecaptchaField()
    body = StringField('Message',
                       [DataRequired(),
                        Length(min=4, message='Your message is too short.')])
    submit = SubmitField('Submit')
