from app import app
import logging
if __name__ == "__main__":

    logging.getLogger("pymongo").setLevel(logging.WARNING)

    app.run(host="0.0.0.0", port=5000, debug=False)
