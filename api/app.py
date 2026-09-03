# app.py
from flask import Flask, jsonify, request
import asyncio
import os
import threading
import time
from flask_cors import CORS

import psycopg
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FlaskIntegration()],
    environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
    release=os.getenv("SENTRY_RELEASE"),
    traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
    send_default_pii=os.getenv("SENTRY_SEND_DEFAULT_PII", "false").lower() == "true",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
)

app = Flask(__name__)

cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    CORS(app)
else:
    CORS(app, origins=[origin.strip() for origin in cors_origins.split(",")])


def chaos_enabled():
    return os.getenv("ENABLE_CHAOS_ROUTES", "false").lower() == "true"


def chaos_disabled_response():
    return jsonify({"error": "Chaos routes are disabled"}), 404


@app.before_request
def enrich_sentry_scope():
    sentry_sdk.set_tag("service", "bookstore-api")
    sentry_sdk.set_context(
        "bookstore_request",
        {
            "method": request.method,
            "path": request.path,
        },
    )

# Mock data for development - Updated book categories
mock_categories = [
    {"id": "classics", "name": "Classics", "description": "Timeless masterpieces from renowned authors."},
    {"id": "modern", "name": "Modern Literature", "description": "Contemporary works from modern authors."},
    {"id": "poetry", "name": "Poetry", "description": "Beautiful poetry from literary giants."},
    {"id": "fiction", "name": "Fiction", "description": "Fictional works with universal appeal."},
    {"id": "fantasy", "name": "Fantasy", "description": "Magical and fantastical stories."},
    {"id": "science", "name": "Science", "description": "Scientific exploration and discovery."}
]

mock_products = [
    {
        "id": "1", 
        "name": "War and Peace", 
        "author": "Leo Tolstoy",
        "price": 24.99, 
        "categoryId": "classics",
        "category": "Classics",
        "description": "War and Peace is a novel by Leo Tolstoy, published in 1869. It is regarded as one of Tolstoy's finest literary achievements and remains an internationally praised classic of world literature.",
        "imageUrl": "/images/books/war-and-peace-leo-tolstoy.jpg",
        "pages": 1225,
        "published": 1869
    },
    {
        "id": "2", 
        "name": "Anna Karenina", 
        "author": "Leo Tolstoy",
        "price": 19.99, 
        "categoryId": "classics",
        "category": "Classics",
        "description": "Anna Karenina is a novel by Leo Tolstoy, first published in book form in 1878. Widely considered a pinnacle in realist fiction, Tolstoy himself called it his first true novel.",
        "imageUrl": "/images/books/anna-karenina-leo-tolstoy.jpg",
        "pages": 864,
        "published": 1878
    },
    {
        "id": "3", 
        "name": "Crime and Punishment", 
        "author": "Fyodor Dostoevsky",
        "price": 18.99, 
        "categoryId": "classics",
        "category": "Classics",
        "description": "Crime and Punishment focuses on the mental anguish and moral dilemmas of Rodion Raskolnikov, an impoverished ex-student in Saint Petersburg who formulates a plan to kill an unscrupulous pawnbroker for her money.",
        "imageUrl": "/images/books/crime-and-punishment-fyodor-dostoevsky.jpg",
        "pages": 671,
        "published": 1866
    },
    {
        "id": "4", 
        "name": "The Idiot", 
        "author": "Fyodor Dostoevsky",
        "price": 17.99, 
        "categoryId": "classics",
        "category": "Classics",
        "description": "The Idiot is a novel by Fyodor Dostoevsky. It was first published serially in the journal The Russian Messenger in 1868–69. The title is an ironic reference to the central character of the novel, Prince Lev Nikolayevich Myshkin.",
        "imageUrl": "/images/books/the-idiot-fyodor-dostoevsky.jpg",
        "pages": 652,
        "published": 1869
    },
    {
        "id": "5", 
        "name": "Eugene Onegin", 
        "author": "Alexander Pushkin",
        "price": 15.99, 
        "categoryId": "poetry",
        "category": "Poetry",
        "description": "Eugene Onegin is a novel in verse written by Alexander Pushkin. Onegin is considered a classic of literature, and its eponymous protagonist has served as the model for a number of literary heroes.",
        "imageUrl": "/images/books/eugene-onegin-alexander-pushkin.jpg",
        "pages": 224,
        "published": 1833
    },
    {
        "id": "6", 
        "name": "Fathers and Sons", 
        "author": "Ivan Turgenev",
        "price": 16.99, 
        "categoryId": "classics",
        "category": "Classics",
        "description": "Fathers and Sons, also translated more literally as Fathers and Children, is an 1862 novel by Ivan Turgenev, published in Moscow by Grachev & Co. It is one of the most acclaimed novels of the 19th century.",
        "imageUrl": "/images/books/fathers-and-sons-ivan-turgenev.jpg",
        "pages": 226,
        "published": 1862
    },
    {
        "id": "7", 
        "name": "The Master and Margarita", 
        "author": "Mikhail Bulgakov",
        "price": 21.99, 
        "categoryId": "modern",
        "category": "Modern Literature",
        "description": "The Master and Margarita is a novel by Mikhail Bulgakov, written between 1928 and 1940 during Stalin's regime. A censored version was published in Moscow magazine in 1966–1967, after the writer's death.",
        "imageUrl": "/images/books/master-and-margarita-mikhail-bulgakov.jpg",
        "pages": 384,
        "published": 1967
    },
    {
        "id": "8", 
        "name": "The Lower Depths", 
        "author": "Maxim Gorky",
        "price": 14.99, 
        "categoryId": "classics",
        "category": "Classics",
        "description": "The Lower Depths is a play by Maxim Gorky, written in 1902. It was a sensation at the Moscow Art Theatre, and it established Gorky's reputation as one of the leading writers.",
        "imageUrl": "/images/books/the-lower-depths-maxim-gorky.jpg",
        "pages": 115,
        "published": 1902
    },
    {
        "id": "9", 
        "name": "What Dreams May Come", 
        "author": "Richard Matheson",
        "price": 16.99, 
        "categoryId": "modern",
        "category": "Modern",
        "description": "What Dreams May Come is a 1978 novel by Richard Matheson. The plot centers on Chris, a man who dies and goes to Heaven, but descends into Hell to rescue his wife. It was adapted into the 1998 film of the same name.",
        "imageUrl": "/images/books/what-dreams-may-come-richard-matheson.jpg",
        "pages": 288,
        "published": 1978
    },
    {
        "id": "10", 
        "name": "Dracula", 
        "author": "Bram Stoker",
        "price": 14.99, 
        "categoryId": "classics",
        "category": "Classics",
        "description": "Dracula is an 1897 Gothic horror novel by Irish author Bram Stoker. It introduced the character of Count Dracula and established many conventions of subsequent vampire fantasy.",
        "imageUrl": "/images/books/bram-stoker-dracula.jpg",
        "pages": 418,
        "published": 1897
    },
    {
        "id": "14", 
        "name": "Pan's Labyrinth", 
        "author": "Guillermo del Toro",
        "price": 22.99, 
        "categoryId": "fiction",
        "category": "Fiction",
        "description": "Pan's Labyrinth: The Labyrinth of the Faun is a dark fantasy novel written by Guillermo del Toro and Cornelia Funke, based on the acclaimed 2006 film. It takes place in Spain during the summer of 1944 and tells of a young girl who discovers a magical labyrinth.",
        "imageUrl": "/images/books/pan-labyrinth.jpg",
        "pages": 272,
        "published": 2019
    },
    {
        "id": "11", 
        "name": "Harry Potter and the Chamber of Secrets", 
        "author": "J.K. Rowling",
        "price": 18.99, 
        "categoryId": "fiction",
        "category": "Fiction",
        "description": "Harry Potter and the Chamber of Secrets is the second novel in the Harry Potter series, written by J. K. Rowling. The plot follows Harry's second year at Hogwarts School of Witchcraft and Wizardry, during which a series of messages on the walls of the school's corridors warn that the 'Chamber of Secrets' has been opened.",
        "imageUrl": "/images/books/harry-potter-chamber-of-secrets.webp",
        "pages": 352,
        "published": 1998
    },
    {
        "id": "12", 
        "name": "Harry Potter and the Prisoner of Azkaban", 
        "author": "J.K. Rowling",
        "price": 19.99, 
        "categoryId": "fiction",
        "category": "Fiction",
        "description": "Harry Potter and the Prisoner of Azkaban is the third novel in the Harry Potter series, written by J. K. Rowling. The book follows Harry Potter, a young wizard, in his third year at Hogwarts School of Witchcraft and Wizardry.",
        "imageUrl": "/images/books/prisoner-of-azkaban.webp",
        "pages": 448,
        "published": 1999
    },
    {
        "id": "13", 
        "name": "Mysteries of the Universe", 
        "author": "Will Gater",
        "price": 27.99, 
        "categoryId": "fiction",
        "category": "Fiction",
        "description": "Mysteries of the Universe explores the wonders of space, featuring stunning images and detailed explanations about galaxies, stars, planets, and cosmic phenomena.",
        "imageUrl": "/images/books/mysteries-of-the-Universe-by-will-gater.jpg",
        "pages": 224,
        "published": 2020
    }
]

# Mock cart data
mock_cart = []

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(mock_categories)

@app.route('/api/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    category = next((c for c in mock_categories if c['id'] == category_id), None)
    if category:
        return jsonify(category)
    return jsonify({"error": "Category not found"}), 404

@app.route('/api/categories/<category_id>/products', methods=['GET'])
def get_products_by_category(category_id):
    products = [p for p in mock_products if p['categoryId'] == category_id]
    return jsonify(products)

@app.route('/api/products/featured', methods=['GET'])
def get_featured_products():
    # Return a subset of products as featured
    featured_ids = ["1", "3", "7", "11","8"]
    featured = [p for p in mock_products if p['id'] in featured_ids]
    return jsonify(featured)

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in mock_products if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    if os.getenv("SENTRY_CAPTURE_404S", "false").lower() == "true":
        sentry_sdk.capture_message(
            f"Product not found: {product_id}",
            level="warning",
        )
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/cart', methods=['GET'])
def get_cart():
    return jsonify(mock_cart)

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    product_id = data.get('productId')
    quantity = data.get('quantity', 1)
    
    product = next((p for p in mock_products if p['id'] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    # Check if the product is already in the cart
    cart_item = next((item for item in mock_cart if item['id'] == product_id), None)
    if cart_item:
        cart_item['quantity'] += quantity
    else:
        mock_cart.append({
            "id": product_id,
            "name": product['name'],
            "author": product['author'],
            "price": product['price'],
            "quantity": quantity,
            "imageUrl": product['imageUrl']
        })
    
    return jsonify({"success": True})

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.json
    item_id = data.get('itemId')
    quantity = data.get('quantity')
    
    item = next((item for item in mock_cart if item['id'] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found in cart"}), 404
    
    item['quantity'] = quantity
    return jsonify({"success": True})

@app.route('/api/cart/remove/<item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    global mock_cart
    mock_cart = [item for item in mock_cart if item['id'] != item_id]
    return jsonify({"success": True})

@app.route('/api/cart/checkout', methods=['POST'])
def checkout():
    global mock_cart
    # In a real app, we would process payment, create order, etc.
    mock_cart = []
    return jsonify({"success": True})

@app.route('/api/debug-sentry', methods=['GET'])
def debug_sentry():
    division_by_zero = 1 / 0
    return jsonify({"result": division_by_zero})

@app.route('/api/chaos/slow', methods=['GET'])
def chaos_slow():
    if not chaos_enabled():
        return chaos_disabled_response()

    seconds = float(request.args.get("seconds", "3"))
    time.sleep(seconds)
    return jsonify({"slept": seconds})

@app.route('/api/chaos/postgres', methods=['GET'])
def chaos_postgres():
    if not chaos_enabled():
        return chaos_disabled_response()

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://bookstore:bookstore@127.0.0.1:5432/bookstore",
    )
    with psycopg.connect(database_url, connect_timeout=1) as connection:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            result = cursor.fetchone()

    return jsonify({"database": "ok", "result": result[0]})

@app.route('/api/chaos/product/<product_id>', methods=['GET'])
def chaos_missing_product(product_id):
    if not chaos_enabled():
        return chaos_disabled_response()

    product = next((p for p in mock_products if p['id'] == product_id), None)
    if product:
        return jsonify(product)

    sentry_sdk.capture_message(
        f"Chaos product lookup missed: {product_id}",
        level="warning",
    )
    return jsonify({"error": "Product not found", "productId": product_id}), 404

# ---------------------------------------------------------------------------
# Chaos routes below exist to generate specific Sentry event shapes on demand.
# All gated behind ENABLE_CHAOS_ROUTES=true. Never enable in a real deployment.
# ---------------------------------------------------------------------------

# ponytail: module-global list, freed only by restarting the process.
# That is the point - it is the leak.
_leaked = []


@app.route('/api/chaos/recursion', methods=['GET'])
def chaos_recursion():
    """RecursionError -> very deep, truncated stack trace in Sentry."""
    if not chaos_enabled():
        return chaos_disabled_response()

    def descend(n):
        return descend(n + 1)

    descend(0)


@app.route('/api/chaos/thread', methods=['GET'])
def chaos_thread():
    """Exception in a background thread. The HTTP response is a normal 200.

    Sentry's ThreadingIntegration (on by default) reports it, so the event has
    no request context and no matching error status on the transaction.
    """
    if not chaos_enabled():
        return chaos_disabled_response()

    def explode():
        raise RuntimeError("Chaos: background thread failed after response was sent")

    thread = threading.Thread(target=explode, name="chaos-worker", daemon=True)
    thread.start()
    return jsonify({"started": thread.name, "note": "check Sentry, not this response"})


@app.route('/api/chaos/unhandled-async', methods=['GET'])
def chaos_unhandled_async():
    """asyncio task whose exception is never retrieved.

    Without AsyncioIntegration this surfaces only as a stderr warning
    ("Task exception was never retrieved") and NO Sentry event - which is
    exactly the "my async errors are missing" report.
    """
    if not chaos_enabled():
        return chaos_disabled_response()

    async def orphan():
        await asyncio.sleep(0)
        raise ValueError("Chaos: orphaned asyncio task")

    async def main():
        asyncio.ensure_future(orphan())
        await asyncio.sleep(0.05)  # let it fail, never await it

    asyncio.run(main())
    return jsonify({"spawned": True, "note": "exception intentionally not retrieved"})


@app.route('/api/chaos/memory', methods=['GET'])
def chaos_memory():
    """Leak ~mb megabytes per call. Repeat until the container OOMs."""
    if not chaos_enabled():
        return chaos_disabled_response()

    mb = int(request.args.get("mb", "50"))
    _leaked.append(bytearray(mb * 1024 * 1024))
    return jsonify({"leaked_mb": mb, "total_mb": sum(len(b) for b in _leaked) // (1024 * 1024)})


@app.route('/api/chaos/nplusone', methods=['GET'])
def chaos_nplusone():
    """One list query followed by N single-row queries.

    sentry-sdk does not auto-instrument psycopg3, so the db spans below are
    created by hand. Removing them is a useful exercise: the slow endpoint
    stays slow but the trace stops explaining why.
    """
    if not chaos_enabled():
        return chaos_disabled_response()

    rows = int(request.args.get("rows", "25"))
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://bookstore:bookstore@127.0.0.1:5432/bookstore",
    )

    with psycopg.connect(database_url, connect_timeout=5) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "create table if not exists chaos_books "
                "(id int primary key, title text not null)"
            )
            cursor.executemany(
                "insert into chaos_books (id, title) values (%s, %s) "
                "on conflict (id) do nothing",
                [(i, f"Book {i}") for i in range(1, rows + 1)],
            )
            connection.commit()

            with sentry_sdk.start_span(op="db", name="select id from chaos_books"):
                cursor.execute("select id from chaos_books order by id limit %s", (rows,))
                ids = [row[0] for row in cursor.fetchall()]

            titles = []
            for book_id in ids:
                # The N+1: one round trip per id instead of a single IN query.
                with sentry_sdk.start_span(
                    op="db", name="select title from chaos_books where id = %s"
                ):
                    cursor.execute(
                        "select title from chaos_books where id = %s", (book_id,)
                    )
                    titles.append(cursor.fetchone()[0])

    return jsonify({"queries": len(ids) + 1, "titles": titles})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
