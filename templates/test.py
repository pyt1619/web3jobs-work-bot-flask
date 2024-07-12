def generate_page_with_base(title, link):
    content = """
    {% extends 'base.html' %}

    {% block title %}{title}{% endblock %}

    {% block content %}
    <div class="container">
        <h1 class="mt-5">{title}</h1>
        <p>This is the content of the {title} page.</p>
    </div>
    {% endblock %}
    """
    content=content.replace('{title}', title)
    filename = f"{link}.html"
    with open(filename, 'w') as file:
        file.write(content)

if __name__ == "__main__":
    menu_items = [
        ("Статистика по юзерам", "user_statistics"),
        ("Оплаты юзеров", "user_payments"),
        ("Список юзеров", "user_list"),
        ("Написать юзерам", "write_to_users"),
        ("Все вакансии", "all_vacancies"),
        ("Отчеты о работе парсеров", "parser_report"),
        ("Статистика рефералка", "referral_statistics"),
        ("Все промотеры рефералка", "all_promoters"),
        ("Лиды рефералка", "referral_leads"),
        ("Запросы на выплату", "payout_requests"),
        ("Статистика выплат", "payout_statistics")
    ]

    for page_title, page_link in menu_items:
        generate_page_with_base(page_title, page_link)
        print(f"Generated {page_link}.html page with base.")

