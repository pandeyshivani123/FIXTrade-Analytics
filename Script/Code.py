from collections import defaultdict

def analyze_fix_file(file_path):
    order_count = 0  # To count new orders(35=D,AB)
    executed_shares = defaultdict(int)  # Key: Symbol, Value: Total Executed Shares
    ordered_shares = defaultdict(int)  # Key: Symbol, Value: Total Ordered Shares
    working_shares = defaultdict(int)  # Key: Symbol, Value: Open/Working Shares

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        order_occurrences = defaultdict(int)  # Tracking the number of orders for each symbol
        symbol_groups = defaultdict(list)  # Grouping lines by symbol for easier processing

        # Grouping lines by symbol
        for line in lines:
            line = line.replace('', '|')
            fields = {kv.split('=')[0]: kv.split('=')[1] for kv in line.strip().split('|') if '=' in kv}
            symbol = fields.get('55') or fields.get('600')
            if symbol:
                symbol_groups[symbol].append(fields)

        # Process each symbol group independently
        for symbol, group in symbol_groups.items():
            current_order_id = None
            last_execution_qty = 0  # Tracking the last execution quantity for each order
            order_executed_qty = 0  # Tracking cumulative executed shares for each order

            for fields in group:
                # Handling new orders (35=D for single orders or 35=AB for multi-leg)
                if fields.get('35') in ['D', 'AB']:
                    order_count += 1
                    order_qty = int(fields.get('38', 0))
                    ordered_shares[symbol] += order_qty

                    # Finalize the previous order's executed quantity before starting a new one
                    if last_execution_qty > 0:
                        order_executed_qty += last_execution_qty
                        last_execution_qty = 0

                # Handle execution reports (35=8)
                if fields.get('35') == '8':
                    # Update last execution quantity for the symbol if non-zero
                    execution_qty = int(fields.get('14', 0))
                    if execution_qty > 0:
                        last_execution_qty = execution_qty

            # Finalize executed shares for the symbol after processing all lines in the group
            if last_execution_qty > 0:
                order_executed_qty += last_execution_qty

            executed_shares[symbol] += order_executed_qty

        # Calculating working shares for all symbols
        for symbol in ordered_shares:
            working_shares[symbol] = ordered_shares[symbol] - executed_shares[symbol]

        return order_count, executed_shares, working_shares

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return 0, {}, {}
    except PermissionError:
        print(f"Permission denied: {file_path}")
        return 0, {}, {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 0, {}, {}


if __name__ == "__main__":
    file_path = "FIXMSG.txt"

    # Calling the function 
    orders_sent, executed, working = analyze_fix_file(file_path)

    # Solution
    print(f"Total Orders Sent: {orders_sent}")
    print("Total Executed Shares/Contracts per Symbol:")
    for symbol, shares in executed.items():
        print(f"  {symbol}: {shares}")
    print("Total Open/Working Shares per Symbol:")
    for symbol, shares in working.items():
        print(f"  {symbol}: {shares}")
