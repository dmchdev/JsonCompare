import json
import argparse
from robot.libraries.BuiltIn import BuiltIn


class JsonCompare(object):
    def __init__(self, debug=False, keeporder=False, print_to_stdout=False):
        self.debug = debug
        self.keeporder = keeporder
        self.print_to_stdout = print_to_stdout

    def all_expected_data_present_in_actual_data(self,
                                                 expected,
                                                 actual, 
                                                 debug=False, 
                                                 keeporder=False,
                                                 printstdout=False):

        """Given 2 JSON structures, this will determine whether data in the expected is contained
           in the actual. The list order is optional, ignored by default. This assumes the same schema for both JSON
           blobs, so that values in expected can be reached using the same path as in actual. The only deviation is the 
           list order which is ignored by default where present and is controlled by 'keeporder' parameter
           :params expected - JSON structure whose data you expect to see in actual
           :params actual   - JSON structure against which you are comparing.
           :params debug    - enable console output for internal variables like recursively extracted JSON substructures
           :params keeporder - turn list order on
           :params printstdout - turn console output on if you are using this as a standalone application
        """

        self.debug = debug
        self.keeporder = keeporder
        self.print_to_stdout = printstdout
        return self._compare_payloads(expected, actual)    
    

    def _compare_lists(self, collection_list, container_list, tracker):
        self._debug("COLLECTION_LIST: {col} \n CONTAINER_LIST: {con}".format(col=collection_list, con=container_list))    

        if not isinstance(collection_list, list) or not isinstance(container_list, list):
            raise("ARGUMENTS ARE NOT LISTS. UNABLE TO COMPARE")
        
        if collection_list == container_list:
            tracker.append(True)
        else:
            for i in range(0, len(collection_list)):
                if isinstance(collection_list[i], list) and isinstance(container_list[i], list):
                    self._compare_lists(collection_list[i], container_list[i], tracker)
                elif isinstance(collection_list[i], dict) and isinstance(container_list[i], dict):
                    if self.keeporder:
                        self._compare_dictionaries(collection_list[i], container_list[i], tracker)
                    else:
                        dictionary_to_compare_with = self._get_correct_dictionary(collection_list[i], container_list)
                        self._compare_dictionaries(collection_list[i], dictionary_to_compare_with, tracker)
                else:
                    if self.keeporder:
                        try:
                            tracker.append(collection_list[i] == container_list[i])
                            if collection_list[i] != container_list[i]:
                                message = ("\nVALIDATION ERROR:"
                                           "\n  Expected element {el} not present in list {l} at position {p}".format(
                                            el=collection_list[i], l=container_list, p=i))
                                self._print_to_stdout(message)
                                self._log_message(message)
                        except IndexError as ie:
                            tracker.append(False)
                            message = ("\nVALIDATION ERROR:" 
                                       "\n  Element {e} from expected list {el} not present in actual list {al}".format(
                                            e=collection_list[i], el=collection_list, al=container_list))
                            self._log_message(message)
                            self._print_to_stdout(message)
                    else:
                        tracker.append(collection_list[i] in container_list)
                        if collection_list[i] not in container_list:
                            message = ("\nVALIDATION ERROR:"
                                       "\n  Expected element {el} not present in list {l}".format(el=collection_list[i], l=container_list))
                            self._print_to_stdout(message)
                            self._log_message(message)    
    

    def _get_correct_dictionary(self, collection_list_element, container_list):
        self._debug("Collection_list_element: {el}".format(el=collection_list_element))
        match_scores = [0]*len(container_list)
        for i in range(0, len(container_list)):
            for key in collection_list_element:
                if collection_list_element[key] == container_list[i].get(key):
                    match_scores[i] +=1
        self._debug("Element with max SCORE: {el}\n".format(el=container_list[match_scores.index(max(match_scores))]))    

        return container_list[match_scores.index(max(match_scores))]    
    

    def _compare_dictionaries(self, collection_dict, container_dict, tracker):
        self._debug("COLLECTION_DICT: {col} \n CONTAINER_DICT: {con}".format(col=collection_dict, con=container_dict))    

        if not isinstance(collection_dict, dict) or not isinstance(container_dict, dict):
            raise("ARGUMENTS ARE NOT DICTIONARIES. UNABLE TO COMPARE")    

        if collection_dict == container_dict:
            tracker.append(True)   
        else:
            for key in collection_dict:
                if isinstance(collection_dict[key], list) and isinstance(container_dict[key], list):
                    self._compare_lists(collection_dict[key], container_dict[key], tracker)
                elif isinstance(collection_dict[key], dict) and isinstance(container_dict[key], dict):
                    self._compare_dictionaries(collection_dict[key], container_dict[key], tracker)
                else:
                    try:
                        tracker.append(collection_dict[key]==container_dict[key])    

                        if collection_dict[key] != container_dict[key]:
                            message = ("\nVALIDATION ERROR:"
                                       "\n  Expected: {k}:{ev}"
                                       "\n  Actual:   {k}:{av}"
                                       "\n  Location {cd}".format(k=key, ev=collection_dict[key],
                                                            av=container_dict[key], cd=container_dict))
                            self._print_to_stdout(message)
                            self._log_message(message)
                    except KeyError as keyerror:
                        tracker.append(False)
                        message = ("\nVALIDATION ERROR:"
                                   "\n  No key '{k}' present in actual data".format(k=key))
                        self._print_to_stdout(message)
                        self._log_message(message)    
    
    

    def _compare_payloads(self, collection_payload, container_payload):
        tracker = []
        if isinstance(collection_payload,list) and isinstance(container_payload, list):
            self._compare_lists(collection_payload, container_payload, tracker)
            self._debug(tracker)
            return all(tracker)
        elif isinstance(collection_payload, dict) and isinstance(container_payload, dict):
            self._compare_dictionaries(collection_payload, container_payload, tracker)
            self._debug(tracker)
            return all(tracker)
        else:
            raise("UNABLE TO COMPARE JSON STRUCTURES OF DIFFERENT TYPES")    

    def _log_message(self, message):
        BuiltIn().log(message, 'INFO')    

    def _debug(self, message):
        if self.debug:
            self._log_message(message)
            print(message)

    def _print_to_stdout(self, message):
        if self.print_to_stdout:
            print(message)


def _load_json(filename):
    with open(filename, "r") as inputfile:
        jsoncontent = json.load(inputfile)
        return jsoncontent


def _parse_cli_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-c", "--collection",
                        help="Collection filename, you are comparing this against some larger container",
                        default="collection.json",
                        required=False)
    parser.add_argument("-n", "--container",
                        help="Container filename, you are comparing your collection to it",
                        default="container.json",
                        required=False)
    parser.add_argument("-d", "--debug",
                        help="Enable debugging logs",
                        default=False,
                        action="store_true")
    parser.add_argument("-ko", "--keeporder",
                        help="Turn on list order validation",
                        action="store_true")
    parser.add_argument("-p", "--printstdout",
                        help="Enable error output to console",
                        action="store_true")
    args = parser.parse_args()
    global debug
    debug = args.debug
    print(args)
    return args


def main():
    args = _parse_cli_args()
    collection_payload = _load_json(args.collection)
    container_payload = _load_json(args.container)
    comparator = JsonCompare(debug=args.debug, keeporder=args.keeporder)
    print(comparator.all_expected_data_present_in_actual_data(collection_payload, container_payload, keeporder=args.keeporder, printstdout=args.printstdout))

if __name__ == '__main__':
    main()