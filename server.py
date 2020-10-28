from sqli_platform import app

if __name__ == "__main__":
    
    # Disabled reloader to avoid executing database queries twice when initializing the application
    app.run(host="127.0.0.1", debug=True, use_reloader=False)
