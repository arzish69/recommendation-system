def validate_request_data(data, required_fields):
    """Validate that all required fields are present in the request data"""
    return all(field in data for field in required_fields)