import json
from hstest import StageTest, CheckResult, dynamic_test
from main import json_response


class Test(StageTest):
    @dynamic_test
    def test(self):
        # Define the keys that must be present in each VPC dictionary
        required_keys = ["Name", "IPv4CIDR", "State", "IPv6CIDRs", "IsDefault"]
        # Define the expected values for certain keys
        expected_values = {
            "Name": "Hyper-VPC",
            "IPv4CIDR": "172.16.0.0/24",
            "State": "available",
            "IsDefault": False
        }

        try:
            # Attempt to parse the JSON reply from the string
            vpcs = json.loads(json_response)
        except json.JSONDecodeError:
            # If JSON is not valid, return False
            return CheckResult.wrong("The JSON reply is not valid.")

        # Ensure that the reply is a non-empty list
        if not isinstance(vpcs, list) or len(vpcs) == 0:
            return CheckResult.wrong("The JSON reply is not a non-empty list.")

        # Iterate over each VPC in the reply
        for vpc in vpcs:
            # Check if all required keys are in the VPC dictionary
            if not all(key in vpc for key in required_keys):
                return CheckResult.wrong(f"Your output is missing a required key: {', '.join(required_keys)}. Check that you have configured the VPC as specified.")

            # Check if the values for certain keys match the expected values
            for key, value in expected_values.items():
                if vpc.get(key) != value:
                    return CheckResult.wrong(f"Incorrect value for the key {key}. Check that you have configured the VPC as specified.")

            # Check if IPv6CIDRs is a non-empty list of dictionaries
            ipv6cidrs = vpc.get("IPv6CIDRs", [])
            if not isinstance(ipv6cidrs, list) or len(ipv6cidrs) == 0:
                return CheckResult.wrong("Your JSON reply does not contain any IPv6CIDR entries. Check that an IPv6 CIDR block has been associated with your VPC.")

            # Iterate over each IPv6CIDR entry
            for ipv6cidr in ipv6cidrs:
                # Ensure that each entry is a dictionary with required keys and values
                if not isinstance(ipv6cidr, dict):
                    return CheckResult.wrong("You do not have any IPv6CIDR entries in your JSON reply.")
                if "Ipv6CIDR" not in ipv6cidr or not ipv6cidr["Ipv6CIDR"]:
                    return CheckResult.wrong("Your IPv6CIDR entry does not contain a valid IPv6 CIDR block.")
                # Check for the "State" field, allowing for both string and dictionary types
                if "State" not in ipv6cidr:
                    return CheckResult.wrong("Your IPv6CIDR entry does not contain a 'State' field.")
                if isinstance(ipv6cidr["State"], dict):
                    if ipv6cidr["State"].get("State") != "associated":
                        return CheckResult.wrong("Your IPv6CIDR entry is not associated with the VPC.")
                elif isinstance(ipv6cidr["State"], str):
                    if ipv6cidr["State"] != "associated":
                        return CheckResult.wrong("Your IPv6CIDR entry is not associated with the VPC.")
                else:
                    return CheckResult.wrong("Something went wrong with the 'State' field in your IPv6CIDR entry.")

        # if all check passed
        return CheckResult.correct()

