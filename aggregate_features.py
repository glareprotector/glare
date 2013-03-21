from features import *



# if a feature output is to be used for bucket functions, then it has to implement get_value
class get_bucket_mean_feature(feature):
    """
    returns a float.  always returns something
    """
    def _generate(self, bucket):
        total = 0.0
        count = 0
        for item in bucket:
            try:
                total += item
                count += 1
            except my_exceptions.NoFxnValueException:
                pass
        if count == 0:
            return my_data_types.no_value_object()
        else:
            return total / float(count)


class get_bucket_sum_feature(feature):
    """
    returns a float.  always returns something
    """
    def _generate(self, bucket):
        total = 0.0
        for item in bucket:
            try:
                total += item
            except my_exceptions.NoFxnValueException:
                # if there is no value, do nothing
                pass
        return total



class get_bucket_max_feature(feature):

    def _generate(self, bucket):
        max_so_far = my_data_types.no_value_object()
        for item in bucket:
            if not isinstance(max_so_far, my_data_types.no_value_object):
                try:
                    if max_so_far < item:
                        max_so_far = item
                except my_exceptions.NoFxnValueException:
                    pass
            else:
                max_so_far = item
        return ans


class get_bucket_min_feature(feature):

    def _generate(self, bucket):
        max_so_far = my_data_types.no_value_object()
        for item in bucket:
            if not isinstance(max_so_far, my_data_types.no_value_object):
                try:
                    if max_so_far > item:
                        max_so_far = item
                except my_exceptions.NoFxnValueException:
                    pass
            else:
                max_so_far = item
        return ans


class get_bucket_count_feature(feature):
    """
    returns the number of objects in buckets that are not no_value_objects
    """
    def _generate(self, bucket):
        count = 0
        for item in bucket:
            if not isinstance(item, my_data_types.no_value_object):
                count += 1
        return count


class get_bucket_count_nonzero_feature(feature):
    """
    returns 1 if the count of the bucket is > 0.  otherwise, 0
    """

    def _generate(self, bucket):
        count = 0

        for item in bucket:
            if not isinstance(item, my_data_types.no_value_object):
                count += 1
        if count > 0:
            return 1
        else:
            return 0



class get_bucket_label_feature(feature):
    """
    returns no_value_object if no real values in bucket, and a int otherwise.  should not raise any exceptions
    assumes that bucket values are either 0 or 1
    """
    def _generate(self, bucket):

        num_0 = 0
        num_1 = 0
        for item in bucket:
            try:
                if val == 0:
                    num_0 += 1
                elif val == 1:
                    num_1 += 1
                else:
                    raise Exception
            except my_exceptions.NoFxnValueException:
                pass
        if num_0 + num_1 == 0:
            return my_data_types.no_value_object()
        if num_1 > num_0:
            return 1
        else:
            return 0

class get_bucket_label_feature_justone(feature):

    def _generate(self, bucket):

        num_0 = 0
        num_1 = 0
        for item in bucket:
            try:
                if val == 0:
                    num_0 += 1
                elif val == 1:
                    num_1 += 1
                else:
                    raise Exception
            except my_exceptions.NoFxnValueException:
                pass
        if num_0 + num_1 == 0:
            return my_data_types.no_value_object()
        if num_1 > 0:
            return 1
        else:
            return 0

