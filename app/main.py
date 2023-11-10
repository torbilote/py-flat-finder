from app.cars.runner import CarRunner
from app.flats.runner import FlatRunner

if __name__ == "__main__":
    flat_runner = FlatRunner()
    flat_runner.run()
    car_runner = CarRunner()
    car_runner.run()
