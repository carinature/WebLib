import datetime

from flask_wtf import FlaskForm, RecaptchaField
from markupsafe import Markup
from numpy import insert
from wtforms import *
from wtforms.fields.html5 import EmailField
from wtforms.validators import *

from . import models as m  # for the global variables and db constants

# from wtforms import (StringField,
#                      TextAreaField,
#                      SubmitField,
#                      PasswordField,
#                      DateField,
#                      SelectField, validators)
# from wtforms.validators import (DataRequired,
#     # Note there is a distinction between this and DataRequired in that
#     # InputRequired looks that form-input data was provided, and DataRequired looks at the post-coercion data.
#                                 Email,
#                                 EqualTo,
#                                 Length,
#                                 URL, Optional)
from wtforms.widgets import html_params, TextInput

EMPTY_LABEL = ''
EARLIEST_CENTURY = -100
NEWEST_CENTURY = 21


class SearchSubject(FlaskForm):
    subject_keyword_1 = StringField(
        EMPTY_LABEL,
        [DataRequired(), Regexp('^\w+$', message="Field accepts one search word")],
        render_kw={'placeholder': ' Subject'})
    subject_keyword_2 = StringField(
        EMPTY_LABEL,
        [Optional(), Regexp('^\w+$', message="Field accepts one search word")],
        render_kw={'placeholder': '(Optional) Subject'})
    submit_subject = SubmitField(' Search',
                                 render_kw={'class': 'btn-primary', }
                                 #            # 'style': 'float: right',
                                 #            # 'onclick': "alert('Fetching Data...')"
                                 #            }
                                 )

    def __repr__(self):
        return f'SearchSubject:\n' \
               f'   kw_1: "{self.subject_keyword_1.data}\n"' \
               f'   kw_2: "{self.subject_keyword_2.data}\n"' \
               f'   btn pressed? {self.submit_subject.data}'


centuries = [
    (-8, '8 BCE'),
    (-7, '7 BCE'),
    (-6, '6 BCE'),
    (-5, '5 BCE'),
    (-4, '4 BCE'),
    (-3, '3 BCE'),
    (-2, '2 BCE'),
    (-1, '1 BCE'),
    (1, '1 CE'),
    (2, '2 CE'),
    (3, '3 CE'),
    (4, '4 CE'),
    (5, '5 CE'),
    (6, '6 CE'),
    (7, '7 CE'),
    (8, '8 CE')
]
languages = [
    ('', 'Any'),
    ('Aramaic', 'Aramaic'),
    ('Arabic', 'Arabic'),
    ('Greek', 'Greek'),
    ('Hebrew', 'Hebrew'),
    ('Latin', 'Latin'),
    ('Syriac', 'Syriac')
]


class Include(FlaskForm):
    include = StringField(render_kw={'placeholder': ' Subject',
                                     'style': 'margin-left:15px'})


class Exclude(FlaskForm):
    exclude = StringField(render_kw={'placeholder': ' Subject',
                                     'style': 'margin-left:15px'})


def validate_century(field_from):
    print('validate_century validate_century validate_century validate_century')

    def _century_check(form, field_to):
        if field_to.data < field_from.data:
            raise ValidationError('Validation Error: \'to_century\' is smaller than \'from_century\' field.')
            # raise ValueError('Validation Error: \'to_century\' is smaller than \'from_century\' field.')

    return _century_check


class FilterForm(FlaskForm):
    # <!--sub-subject filtering options-->
    includes = FieldList(
        # 'Including ',  # fixme remove *all* [Optional()] ?
        FormField(Include), min_entries=1, label='Includes'
    )
    excludes = FieldList(
        # 'Including ',  # fixme remove *all* [Optional()] ?
        FormField(Exclude), min_entries=1, label='Excludes'
    )

    # <!--text and reference filtering options-->
    # Dont delete this: https://gist.github.com/Overdese/abebc48e878662377988
    from_century = SelectField('From ', id="from-century-dl",
                               # validators=[],
                               render_kw={'style': ' float:right;'},
                               # choices=centuries,
                               choices=[(-21, 'Any'), *centuries],
                               coerce=int
                               )
    to_century = SelectField('To ', id="to-century-dl",
                             validators=[validate_century(field_from=from_century)],
                             render_kw={'style': ' float:right;'},
                             # choices=centuries,
                             choices=[tuple((21, 'Any')), *centuries],
                             coerce=int
                             )
    language = SelectField('Language ', id="language-dl",
                           render_kw={'style': ' float:right;'},
                           choices=languages,
                           # render_kw={'style': 'margin-left: 20px; float: right'},
                           )
    ancient_author = StringField('Ancient Author ',
                                 render_kw={'placeholder': ' (In English)'}
                                 )
    ancient_title = StringField('Ancient Work-Title ',
                                render_kw={'placeholder': ' (In English)'}
                                )
    reference = StringField('Reference ',
                            render_kw={
                                'placeholder': '(e.g., 1.1 for chapter 1 verse 1, or leave empty for whole work)'}
                            )
    fetch_full = BooleanField('   Fetch full text', id='fetch_full_chkbox',
                              render_kw={
                                  # 'class': 'inline-radio',
                                  # 'style': 'padding;',
                                  # 'onClick': 'displayWarningFetchAllChkbx()',
                                  'onClick':  # todo remove alert?
                                      "alert('Attention! Checking this box will attempt full text fetching, which can result in very highly loading times.')"}
                              )
    attention_label = Label(
        text='(Attention: Checking this box will attempt full text fetching,'
             '\nwhich can result in very highly loading times.)',
        field_id=fetch_full)
    fetch_results = SubmitField('Fetch Results',
                                render_kw={'class': 'btn btn-lg btn-primary',
                                           'style': 'margin-right: 5%; padding:1rem 4rem 1rem 4rem; position: sticky; float: right',
                                           # 'onclick': "alert('Fetching Data...')"
                                           }
                                )

    # clean_button = ('Clear all fields')

    def __repr__(self):
        strtr = f'SearchSubject:' \
                f'\n   includes: '
        for i in self.includes.data:
            strtr += f" {i['include']} "
        strtr += f'\n   excludes: '
        for i in self.excludes.data:
            strtr += f" {i['exclude']} "
        strtr += f'\n' \
                 f'   from_century: "{self.from_century.data}\n"' \
                 f'   to_century: "{self.to_century.data}\n"' \
                 f'   language: "{self.language.data}\n"' \
                 f'   ancient_author: "{self.ancient_author.data}\n"' \
                 f'   reference: "{self.reference.data}\n"' \
                 f'   ancient_title: "{self.ancient_title.data}\n"' \
                 f'   fetch_full? {self.fetch_full.data}'

        return strtr


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
    submit_reference = SubmitField('Submit',
                                   # render_kw={'class': 'btn btn-lg btn-primary',
                                   #            # 'style': 'float: right',
                                   #            # 'onclick': "alert('Fetching Data...')"
                                   #            }
                                   )


class SearchTypeChoice(FlaskForm):
    r_field = RadioField(
        'Label',
        choices=[(1, 'Search by Subject'), (0, 'Search by Reference')],
        render_kw={'class': 'inline-radio', 'style': ''}
        # render_kw={'class': 'inline-radio',
        # 'style': 'font-size:1.5em; vertical-align: middle; horizontal-align: middle;text-align: center'}
    )


class SignupForm(FlaskForm):
    # sign up for updates
    email = EmailField('Email', [DataRequired(), Email()],
                       render_kw={'id': 'email_field',
                                  'placeholder': ' e.g. username@email.edu '})
    submit_email = SubmitField('Submit',
                               render_kw={'class': 'btn btn-default',
                                          'id': 'lala',
                                          'style': 'background-color: var(--secondary-color-light);',
                                          }
                               )

#     """Sign up for a user account."""
#     # email = StringField('Email', [
#     #     Email(message='Not a valid email address.'),
#     #     DataRequired()])
#     # background_color = ColorField() # from wtforms_components import If, ColorField
#     password = PasswordField('Password', [
#         DataRequired(message="Please enter a password."),
#     ])
#     confirmPassword = PasswordField('Repeat Password', [
#         EqualTo(password, message='Passwords must match.')
#     ])
#     title = SelectField('Title', [DataRequired()],
#                         choices=[('Farmer', 'farmer'),
#                                  ('Corrupt Politician', 'politician'),
#                                  ('No-nonsense City Cop', 'cop'),
#                                  ('Professional Rocket League Player', 'rocket'),
#                                  ('Lonely Guy At A Diner', 'lonely'),
#                                  ('Pokemon Trainer', 'pokemon')])
#     website = StringField('Website', validators=[URL()])
#     birthday = DateField('Your Birthday')
#     recaptcha = RecaptchaField()
#     body = StringField('Message',
#                        [DataRequired(),
#                         Length(min=4, message='Your message is too short.')])
#     submit = SubmitField('Submit')
#     # ,validators=[
#     # If(lambda form, field: form.user_id.data, Email())])
