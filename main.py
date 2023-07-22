import os
import functions_framework

from vendors import RamiLevyOrders


def main():
    service = RamiLevyOrders(os.getenv("USER1"), os.getenv("PASSWORD1"))
    service.login()
    service.collect_orders()
    print("lalalgg")


@functions_framework.cloud_event
def collect_orders(cloud_event):
    main()


if __name__ == "__main__":
    main()
