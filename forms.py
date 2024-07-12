from flask_wtf import FlaskForm
from wtforms import BooleanField, TextAreaField, SubmitField, StringField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class SendMsgForm(FlaskForm):
    paid_year = BooleanField('Платный (на год)')
    paid_monthly = BooleanField('Платный (на месяц)')
    trial = BooleanField('Триал')
    promo = BooleanField('Промо')
    free = BooleanField('Бесплатный')
    msg = TextAreaField('Сообщение')
    submit = SubmitField('Отправить')
    image = FileField('Загрузить изображение', validators=[FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')])


class UserFilter(FlaskForm):
    paid_year = BooleanField('Платный (на год)')
    paid_monthly = BooleanField('Платный (на месяц)')
    trial = BooleanField('Триал')
    promo = BooleanField('Промо')
    free = BooleanField('Бесплатный')
    submit = SubmitField('Фильтровать')

class CategoryFilterForm(FlaskForm):
    title_search = StringField('Поиск по названию вакансии:')
    company_search = StringField('Поиск по названию компании:')
    category_customer_support = BooleanField('Customer Support')
    category_design = BooleanField('Design')
    category_technical = BooleanField('Technical')
    category_finance = BooleanField('Finance')
    category_marketing = BooleanField('Marketing')
    category_nontech = BooleanField('Non-Tech')
    category_operations = BooleanField('Operations')
    category_product_surin = BooleanField('Product Surin')
    category_other = BooleanField('Other')
    submit_category_filter = SubmitField('Применить фильтр')
