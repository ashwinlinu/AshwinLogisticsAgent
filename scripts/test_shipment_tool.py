import asyncio

from app.tools.shipment_tools import get_shipment_status


async def main():

    print("=" * 60)
    print("SHIPMENT TOOL TEST")
    print("=" * 60)

    result = await get_shipment_status.ainvoke(
        {
            "shipment_id": "SHP-1001"
        }
    )

    print("\nSHP-1001:")
    print(result)

    result = await get_shipment_status.ainvoke(
        {
            "shipment_id": "SHP-9999"
        }
    )

    print("\nSHP-9999:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())