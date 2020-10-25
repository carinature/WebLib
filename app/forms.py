from flask_wtf import FlaskForm, RecaptchaField
from markupsafe import Markup
from wtforms import *
from wtforms.validators import *

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



class MyTextInput(TextInput):
    def __init__(self, error_class=u'has_errors'):
        super(MyTextInput, self).__init__()
        self.error_class = error_class

    def __call__(self, field, **kwargs):
        if field.errors:
            c = kwargs.pop('class', '') or kwargs.pop('class_', '')
            kwargs['class'] = u'%s %s' % (self.error_class, c)
        return super(MyTextInput, self).__call__(field, **kwargs)


def select_multi_checkbox(field, ul_class='', **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    html = [u'<ul %s>' % html_params(id=field_id, class_=ul_class)]
    for value, label, checked in field.iter_choices():
        choice_id = u'%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append(u'<li><input %s /> ' % html_options(**options))
        html.append(u'<label %s>%s</label></li>')
    html.append(u'</ul>')
    return u''.join(html)

class TelephoneForm(Form):
    # country_code = IntegerField('Country Code', [validators.required()])
    # area_code = IntegerField('Area Code/Exchange', [validators.required()])
    # number = StringField('Number')
    check:BooleanField = BooleanField('check')
    bla = Label(text='lbl', field_id='ls')

    def __init__(self, name='name___', **kwargs):
        super().__init__(**kwargs)
        self.check = BooleanField(label=name)
        self.bla = Label(text=name, field_id=kwargs)


class ContactForm(FlaskForm):
    first_name = StringField()
    last_name = StringField()
    mobile_phone = FormField(TelephoneForm)
    office_phone = FormField(TelephoneForm)
    # authors = FieldList(StringField('Name', [validators.required()]))
    # authors = FieldList(FormField(BooleanField))

    telephoneForm = FieldList(FormField(TelephoneForm))


class ListWidget(object):
    """
    Renders a list of fields as a `ul` list.
    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.

    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = ['<ul style=\'list-style-type: none;\'  %s >' % (html_params(**kwargs))]
        for subfield in field:
            html.append('<li>%s %s</li>' % (subfield(), subfield.label))
        html.append('</ul>')
        return Markup(''.join(html))

#
# class Chkbx(FlaskForm):
#     bla = BooleanField(label='remember_me', default=False)
#     # def __init__(self):
#     #     super(Chkbx, self).__init__(*args, **kwargs)


class MultiCheckboxField(SelectMultipleField):
    def __init__(self, *args, **kwargs):
        # super(SelectMultipleField, self).__init__()
        super().__init__(*args, **kwargs)
        self.choices=kwargs['choices']

    widget = ListWidget()
    option_widget = widgets.CheckboxInput()


class SimpleForm(FlaskForm):
    checkbox = BooleanField('Select All')

    def __init__(self, string_of_files):
        super().__init__()

        # string_of_files = kwargs['choices']

        # string_of_files = ['one\r\ntwo\r\nthree\r\n']
        # list_of_files = string_of_files[0].split()
        # # create a list of value/description tuples
        # files = [(1,1),(2,2),(3,3)]
        # files = [(x, x) for x in list_of_files]
        self.example = MultiCheckboxField('Label', choices=string_of_files)

    files = [(1,1),(2,2),(3,3)]
    example = MultiCheckboxField('Label', choices=files)


class PurchaseForm(Form):
    item_class = widgets.CheckboxInput()
    transaction_items = FieldList(FormField(item_class),
                                  label='items',
                                  min_entries=1)

    def __init__(self, item_class, *args, **kwargs):
       super().__init__(*args, **kwargs, field=FormField(self.item_class))
       self.item_class = item_class
       self.transaction_items = FieldList(FormField(self.item_class),
                                           label='items',
                                           min_entries=1)


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
    submit_subject = SubmitField('Submit',
                                 # render_kw={'class': 'btn btn-lg btn-primary',
                                 #            # 'style': 'float: right',
                                 #            # 'onclick': "alert('Fetching Data...')"
                                 #            }
                                 )


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


centuries = [('Any', 'Any'),
             ('8 BCE', '8 BCE'),
             ('7 BCE', '7 BCE'),
             ('6 BCE', '6 BCE'),
             ('5 BCE', '5 BCE'),
             ('4 BCE', '4 BCE'),
             ('3 BCE', '3 BCE'),
             ('2 BCE', '2 BCE'),
             ('1 BCE', '1 BCE'),
             ('1 CE', '1 CE'),
             ('2 CE', '2 CE'),
             ('3 CE', '3 CE'),
             ('4 CE', '4 CE'),
             ('5 CE', '5 CE'),
             ('6 CE', '6 CE'),
             ('7 CE', '7 CE'),
             ('8 CE', '8 CE')]
languages = [
    ('Any', 'Any'),
    ('Aramaic', 'Aramaic'),
    ('Arabic', 'Arabic'),
    ('Greek', 'Greek'),
    ('Hebrew', 'Hebrew'),
    ('Latin', 'Latin'),
    ('Syriac', 'Syriac')
]


class FilterForm(FlaskForm):
    """Sign up for a user account."""
    # email = StringField('Email', [
    #     Email(message='Not a valid email address.'),
    #     DataRequired()])

    # <!--sub-subject filtering options-->
    include = StringField('Including ',  # fixme remove *all* [Optional()] ?
                          render_kw={'placeholder': 'Subject'}
                          )
    exclude = StringField('Excluding ',
                          render_kw={'placeholder': 'Subject'}
                          )

    # <!--text and reference filtering options-->
    # Dont delete this: https://gist.github.com/Overdese/abebc48e878662377988
    from_century = SelectField('From ', id="from-century-dl",
                               choices=centuries,
                               )
    to_century = SelectField('To ', id="to-century-dl",
                             choices=centuries,
                             )
    language = SelectField('Language ', id="language-dl",
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
    fetch_full = BooleanField('Fetch full text',
                              render_kw={'class': 'inline-radio', 'style': ''}
                              )
    attention_label = Label(text='(Attention: Check this box will to attempt full text fetching,'
                                 + ' which can result in very highly loading times.)', field_id=fetch_full)
    # submit = SubmitField('Fetch Results',
    #                      render_kw={'class': 'btn btn-lg btn-primary',
    #                      'style': 'margin-right: 5%; padding:1rem 4rem 1rem 4rem; position: sticky; float: right',
    #                                 'onclick': "alert('Fetching Data...')"}
    #                      )


class SearchTypeChoice(FlaskForm):
    r_field = RadioField(
        'Label',
        choices=[(1, 'Search by Subject'), (0, 'Search by Reference')],
        render_kw={'class': 'inline-radio', 'style': ''}
        # render_kw={'class': 'inline-radio',
        # 'style': 'font-size:1.5em; vertical-align: middle; horizontal-align: middle;text-align: center'}
    )


class SignupForm(FlaskForm):
    """Sign up for a user account."""
    # email = StringField('Email', [
    #     Email(message='Not a valid email address.'),
    #     DataRequired()])
    # background_color = ColorField() # from wtforms_components import If, ColorField
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
    # ,validators=[
    # If(lambda form, field: form.user_id.data, Email())])
