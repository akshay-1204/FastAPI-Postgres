from Tables.customers import create_customers_table
from Tables.authors import create_authors_table
from Tables.categories import create_categories_table
from Tables.books import create_books_table
from Tables.orders import create_orders_table
from Tables.order_items import create_order_items_table

from CURD.customer_crud import insert_customers
from CURD.author_crud import insert_authors
from CURD.category_crud import insert_categories
from CURD.book_crud import insert_books
from CURD.order_crud import insert_orders
from CURD.order_item_crud import insert_order_items

from Retrieval.customer_retrieval import get_all_customers, get_customer_by_id, get_customer_by_email, get_total_orders_by_customer, get_total_spent_by_customer

from Retrieval.author_retrieval import get_all_authors, get_author_by_id, get_top_authors_by_sales

from Retrieval.category_retrieval import get_all_categories, get_revenue_by_category, get_average_book_price_by_category

from Retrieval.book_retrieval import get_all_books, get_book_by_id, get_book_by_isbn, search_books_by_title, get_books_by_category, get_books_by_author, get_books_in_price_range, get_books_in_stock, get_out_of_stock_books, get_books_published_between, get_low_stock_books, get_books_paginated

from Retrieval.order_retrieval import get_orders_by_status, get_orders_by_customer, get_orders_between_dates, get_orders_paginated

from Retrieval.join_retrieval import get_book_details_with_author_category, get_order_with_items, get_customer_order_history, get_all_orders_with_customer_name

from Retrieval.reports import get_best_selling_books, get_monthly_order_summary


if __name__ == "__main__":
    create_customers_table()
    create_authors_table()
    create_categories_table()
    create_books_table()
    create_orders_table()
    create_order_items_table()

    choice = input(
        "\nWhat do you want to do?\n"
        "1. Insert\n"
        "2. Retrieval\n"
        "3. Exit\n"
        "Enter your choice: "
    ).strip()

    if choice == "1":

        table = input(
            "\nWhat do you want to insert into the database "
            "(authors, categories, books, orders, order_items, customers): "
        ).strip().lower()

        if table == "customers":
            insert_customers()

        elif table == "authors":
            insert_authors()

        elif table == "categories":
            insert_categories()

        elif table == "books":
            insert_books()

        elif table == "orders":
            insert_orders()

        elif table == "order_items":
            insert_order_items()

        else:
            print("Invalid table name.")

    
    elif choice == "2":

        retrieval = input(
            "\nWhat do you want to retrieve?\n"
            "\n"
            "1. All Customers\n"
            "2. Customer by ID\n"
            "3. Customer by Email\n"
            "4. All Books\n"
            "5. Book by ID\n"
            "6. Book by ISBN\n"
            "7. All Authors\n"
            "8. Author by ID\n"
            "9. All Categories\n"
            "10. Orders by Status\n"
            "11. Search Books by Title\n"
            "12. Books by Category ID\n"
            "13. Books by Author ID\n"
            "14. Books in Price Range\n"
            "15. Books in Stock\n"
            "16. Out-of-Stock Books\n"
            "17. Books Published Between Years\n"
            "18. Orders by Customer\n"
            "19. Orders Between Dates\n"
            "20. Book Details with Author and Category\n"
            "21. Order with Items\n"
            "22. Customer Order History\n"
            "23. All Orders with Customer Name\n"
            "24. Total Orders by Customer\n"
            "25. Total Spent by Customer\n"
            "26. Best Selling Books\n"
            "27. Revenue by Category\n"
            "28. Top Authors by Sales\n"
            "29. Average Book Price by Category\n"
            "30. Low Stock Books\n"
            "31. Monthly Order Summary\n"
            "32. Books Pagination\n"
            "33. Orders Pagination\n"
            "\n"
            "Enter your choice: "
        ).strip()

        # 1. All Customers
        if retrieval == "1":
            get_all_customers()

        # 2. Customer by ID
        elif retrieval == "2":
            customer_id = int(input("Enter customer ID: "))
            get_customer_by_id(customer_id)

        # 3. Customer by Email
        elif retrieval == "3":
            email = input("Enter customer email: ")
            get_customer_by_email(email)

        # 4. All Books
        elif retrieval == "4":
            get_all_books()

        # 5. Book by ID
        elif retrieval == "5":
            book_id = int(input("Enter book ID: "))
            get_book_by_id(book_id)

        # 6. Book by ISBN
        elif retrieval == "6":
            isbn = input("Enter book ISBN: ")
            get_book_by_isbn(isbn)

        # 7. All Authors
        elif retrieval == "7":
            get_all_authors()

        # 8. Author by ID
        elif retrieval == "8":
            author_id = int(input("Enter author ID: "))
            get_author_by_id(author_id)

        # 9. All Categories
        elif retrieval == "9":
            get_all_categories()

        # 10. Orders by Status
        elif retrieval == "10":
            status = input("Enter order status: ")
            get_orders_by_status(status)

        # 11. Search Books by Title
        elif retrieval == "11":
            keyword = input("Enter book title keyword: ")
            search_books_by_title(keyword)

        # 12. Books by Category ID
        elif retrieval == "12":
            category_id = int(input("Enter category ID: "))
            get_books_by_category(category_id)

        # 13. Books by Author ID
        elif retrieval == "13":
            author_id = int(input("Enter author ID: "))
            get_books_by_author(author_id)

        # 14. Books in Price Range
        elif retrieval == "14":
            min_price = float(input("Enter minimum price: "))
            max_price = float(input("Enter maximum price: "))
            get_books_in_price_range(min_price, max_price)

        # 15. Books in Stock
        elif retrieval == "15":
            get_books_in_stock()

        # 16. Out-of-Stock Books
        elif retrieval == "16":
            get_out_of_stock_books()

        # 17. Books Published Between Years
        elif retrieval == "17":
            start_year = int(input("Enter starting year: "))
            end_year = int(input("Enter ending year: "))
            get_books_published_between(start_year, end_year)

        # 18. Orders by Customer
        elif retrieval == "18":
            customer_id = int(input("Enter customer ID: "))
            get_orders_by_customer(customer_id)

        # 19. Orders Between Dates
        elif retrieval == "19":
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            get_orders_between_dates(start_date, end_date)

        # 20. Book Details with Author and Category
        elif retrieval == "20":
            book_id = int(input("Enter book ID: "))
            get_book_details_with_author_category(book_id)

        # 21. Order with Items
        elif retrieval == "21":
            order_id = int(input("Enter order ID: "))
            get_order_with_items(order_id)

        # 22. Customer Order History
        elif retrieval == "22":
            customer_id = int(input("Enter customer ID: "))
            get_customer_order_history(customer_id)

        # 23. All Orders with Customer Name
        elif retrieval == "23":
            get_all_orders_with_customer_name()

        # 24. Total Orders by Customer
        elif retrieval == "24":
            customer_id = int(input("Enter customer ID: "))
            get_total_orders_by_customer(customer_id)

        # 25. Total Spent by Customer
        elif retrieval == "25":
            customer_id = int(input("Enter customer ID: "))
            get_total_spent_by_customer(customer_id)

        # 26. Best Selling Books
        elif retrieval == "26":
            limit = int(input("Enter number of books: "))
            get_best_selling_books(limit)

        # 27. Revenue by Category
        elif retrieval == "27":
            get_revenue_by_category()

        # 28. Top Authors by Sales
        elif retrieval == "28":
            limit = int(input("Enter number of authors: "))
            get_top_authors_by_sales(limit)

        # 29. Average Book Price by Category
        elif retrieval == "29":
            get_average_book_price_by_category()

        # 30. Low Stock Books
        elif retrieval == "30":
            threshold = int(input("Enter stock threshold: "))
            get_low_stock_books(threshold)

        # 31. Monthly Order Summary
        elif retrieval == "31":
            get_monthly_order_summary()

        # 32. Books Pagination
        elif retrieval == "32":
            limit = int(input("Enter number of books: "))
            offset = int(input("Enter offset: "))
            get_books_paginated(limit, offset)

        # 33. Orders Pagination
        elif retrieval == "33":
            limit = int(input("Enter number of orders: "))
            offset = int(input("Enter offset: "))
            get_orders_paginated(limit, offset)

        else:
            print("Invalid retrieval choice.")

    # ---------------- EXIT ----------------

    elif choice == "3":
        print("Exiting program...")

    else:
        print("Invalid choice.")