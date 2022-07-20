# Non-local imports
import mypytoolkit as kit
from numpy import isin

# Project modules
import delivery
import allocation
from allocation import alpaca, Config
import utils


def _account_summary() -> str:
    """Creates an account summary string for use in `deliver_update`."""
    # Positions
    account_positions = alpaca.list_positions()
    positions: dict[str, dict[str, float]] = {}
    for position in account_positions:
        positions[position.symbol] = {
            "Market Value": round(float(position.market_value), 2),
            "Unrealized Profit": round(float(position.unrealized_pl), 2)
        }

    positions_str = ""
    for symbol, attributes in positions.items():
        positions_str += (
            f"{symbol} is "
            f"{'up $' if attributes['Unrealized Profit'] > 0 else 'down -$'}"
            f"{abs(attributes['Unrealized Profit'])} in total, with a market value of "
            f"${attributes['Market Value']}.\n"
        )

    summary = (
        f"The account is on a moderate "
        f"total market value is ${utils.account_equity(rounding=2)}. "
        "Below are all positions managed in the account.\n\n"
        f"{positions_str}"
    )

    return summary


def deliver_update(
    allocations: dict[str, float], 
    rebalances: dict[str, float] | str
) -> None:
    """Texts an update of all that was done. Eventually, this will use email."""
    # If both dictionaries are empty
    if not allocations and not rebalances:
        update = "No actions were taken today."
        delivery.text_me(update)
        delivery.email_me(update, subject="Allocator Daily Report")
        return

    sector_from_symbol = {val[1]: key for key, val in allocation.allocation.items()}

    allocations_str = "" if allocations else "No allocations were made today."
    for symbol, amount in allocations.items():
        allocations_str += f"Allocated ${amount} of cash to {sector_from_symbol[symbol]}.\n"

    rebalances_str = "" if rebalances else "No positions were rebalanced today."
    if isinstance(rebalances, str):
        rebalances_str = rebalances
    elif isinstance(rebalances, dict):
        for symbol, delta in rebalances.items():
            if delta < 0:
                rebalances_str += f"Added ${abs(delta)} to {sector_from_symbol[symbol]}.\n"
            elif delta > 0:
                rebalances_str += f"Removed ${abs(delta)} from {sector_from_symbol[symbol]}.\n"

    update = (
        f"The following is a summary report of actions taken/attempted by Allocator "
        f"today, {kit.today_date()}.\n\n"
        "Allocations:\n"
        f"{allocations_str}\n\n"
        "Rebalances:\n"
        f"{rebalances_str}"
        ""
    )

    delivery.text_me(update)
    delivery.email_me(update, subject="Allocator Daily Report")

if __name__ == '__main__':
    print(_account_summary())
