
from website import create_app

app = create_app()

if __name__ == '__main__':
    # run the app in debug mode to auto-reload
    # app.run(debug=True)
    app.run(debug=True, port=5001)
