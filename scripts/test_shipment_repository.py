import asyncio

from app.db.repositories.shipment_repository import shipment_repository


async def main():

    print("=" * 60)
    print("SHIPMENT REPOSITORY TEST")
    print("=" * 60)

    shipment = await shipment_repository.get_shipment("SHP-1001")

    print("\nSHP-1001:")
    print(shipment)

    shipment = await shipment_repository.get_shipment("SHP-1002")

    print("\nSHP-1002:")
    print(shipment)

    shipment = await shipment_repository.get_shipment("SHP-9999")

    print("\nSHP-9999:")
    print(shipment)


if __name__ == "__main__":
    asyncio.run(main())