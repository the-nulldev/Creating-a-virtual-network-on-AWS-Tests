import json
from hstest import StageTest, CheckResult, dynamic_test
from main import json_reply


class Test(StageTest):
    @dynamic_test
    def test(self):

        # Define the keys that must be present in each Subnet dictionary
        required_keys = ["Name", "IPv4CIDR", "AvailabilityZone", "MapPublicIpOnLaunch"]
        # Define the expected values for certain keys
        expected_values = {
            "Name": "Hyper-Subnet",
            "IPv4CIDR": "172.16.0.0/28",
            "AvailabilityZone": "us-east-1a",
            "MapPublicIpOnLaunch": True
        }

        try:
            # Attempt to parse the JSON reply from the string
            subnets = json.loads(json_reply)
        except json.JSONDecodeError:
            # If JSON is not valid, return False
            return CheckResult.wrong("The JSON reply is not valid.")

        # Ensure that the reply is a non-empty list
        if not isinstance(subnets, list) or len(subnets) == 0:
            return CheckResult.wrong("The JSON reply is not a non-empty list.")

        # Iterate over each Subnet in the reply
        for subnet in subnets:
            # Check if all required keys are in the Subnet dictionary
            if not all(key in subnet for key in required_keys):
                return CheckResult.wrong(f"Your output is missing a required key: {', '.join(required_keys)}.")

            # Check if the values for certain keys match the expected values
            for key, value in expected_values.items():
                # AWS CLI returns booleans in lowercase (true/false)
                if key == "MapPublicIpOnLaunch":
                    if str(subnet.get(key, "")).lower() != str(value).lower():
                        return CheckResult.wrong(f"The value for the key {key} should be {value}, but is {subnet.get(key, '')}. Ensure that you configured the subnet as specified.")
                elif subnet.get(key) != value:
                    return CheckResult.wrong(f"Incorrect value for the key {key}. Ensure that you configured the subnet as specified.")
        return CheckResult.correct()


if __name__ == '__main__':
    Test().run_tests()
