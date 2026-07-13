# Stage 7 (side-quest): async fundamentals - proving concurrent waiting
# beats sequential waiting. time.sleep() / asyncio.sleep() simulate a
# slow API call (e.g. waiting on a network response) without depending
# on any external service's uptime.
from time import time, sleep
import asyncio


def run_sequential():
    start = time()
    # Simulate waiting on 3 slow "API calls" of 3, 2, and 1 seconds,
    # one after another. time.sleep() blocks everything - nothing
    # else can happen while it waits.
    for delay in [3, 2, 1]:
        sleep(delay)
        print(f"finished a {delay}s call")
    end = time()
    print(f"Sequential execution time: {end - start:.2f}s")


async def run_one(delay):
    # await pauses just THIS function here and hands control back to
    # the event loop, so other async tasks can run during the wait -
    # unlike time.sleep(), which blocks the whole program.
    await asyncio.sleep(delay)
    print(f"finished a {delay}s call")


async def run_concurrent():
    start = time()
    # Build 3 tasks, then start all of them at once via gather().
    # *tasks unpacks the list into gather(task1, task2, task3) form.
    tasks = [run_one(delay) for delay in [3, 2, 1]]
    await asyncio.gather(*tasks)
    end = time()
    print(f"Concurrent execution time: {end - start:.2f}s")
    # Note: calls finish in order of THEIR OWN delay (1s, 2s, 3s),
    # not the order they were started in - proof they ran
    # concurrently rather than one waiting for the previous to finish.


if __name__ == "__main__":
    run_sequential()
    # async functions can't be called directly - asyncio.run() starts
    # the event loop needed to actually execute them.
    asyncio.run(run_concurrent())
