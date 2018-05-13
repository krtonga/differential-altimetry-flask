from app import app, db
from app.models import User, Sensor, Point

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Sensor': Sensor, 'Point': Point}

if __name__ == "__main__":
    app.run(host='0.0.0.0')

    
