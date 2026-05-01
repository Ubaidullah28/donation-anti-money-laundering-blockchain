THRESHOLD = 100000
FREQUENCY_LIMIT = 5

def check_aml(donor, amount, recent_transactions):
    """
    Check for Anti-Money Laundering violations:
    - Amount exceeds threshold
    - Donor has made too many recent transactions
    """
    if amount > THRESHOLD:
        return True

    if recent_transactions.count(donor) > FREQUENCY_LIMIT:
        return True

    return False


def check_aml_approvals(amount, approvals):
    """
    Check AML for fund requests based on amount and approvals
    """
    if amount > THRESHOLD and approvals < 2:
        return True
    return False