from features import *



# if a feature output is to be used for bucket functions, then it has to implement get_value
class get_bucket_mean_feature(feature):
    """
    only assumes that bucket is iterable, and items have implement the base_single_ordinal_single_value_ordered_object
    """
    def _generate(self, bucket):
        total = 0.0
        count = 0
        for item in bucket:
            try:
                total += item.get_value()
                count += 1
            except my_exceptions.NoFxnValueException:
                # if there is no value, get_value will raise exception
                pass
        if count == 0:
            return my_data_types.no_value_object()
        else:
            return sv_float(total / float(count))


class get_bucket_sum_feature(feature):
    """
    only assumes that bucket is iterable, and items have implement the base_single_ordinal_single_value_ordered_object
    """
    def _generate(self, bucket):
        total = 0.0
        for item in bucket:
            try:
                total += item.get_value()
            except my_exceptions.NoFxnValueException:
                # if there is no value, get_value will raise exception
                pass
        return sv_float(total)



class get_bucket_max_feature(feature):

    def _generate(self, bucket):
        max_so_far = None
        ans = my_data_types.no_value_object()
        for item in bucket:
            try:
                val = item.get_ordinal()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                if max_so_far == None:
                    max_so_far = val
                    ans = item
                elif val > max_so_far:
                    max_so_far = val
                    ans = item
        return ans


class get_bucket_min_feature(feature):

    def _generate(self, bucket):
        min_so_far = None
        ans = my_data_types.no_value_object()
        for item in bucket:
            try:
                val = item.get_ordinal()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                if min_so_far == None:
                    min_so_far = val
                    ans = item
                elif val < min_so_far:
                    min_so_far = val
                    ans = item
        return ans


class get_bucket_count_feature(feature):

    def _generate(self, bucket):
        count = 0
        for item in bucket:
            try:
                item.get_value()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                count += 1
        return sv_int(count)




class get_bucket_count_nonzero_feature(feature):

    def _generate(self, bucket):
        count = 0

        for item in bucket:
            try:
                item.get_value()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                count += 1
        if count > 0:
            return sv_int(1)
        else:
            return sv_int(0)



class get_bucket_label_feature(feature):

    def _generate(self, bucket):

        num_0 = 0
        num_1 = 0
        for item in bucket:
            try:
                val = item.get_value()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                if val == 0:
                    num_0 += 1
                else:
                    num_1 += 1
        if num_0 + num_1 == 0:
            return my_data_types.no_value_object()
        if num_1 > num_0:
            return sv_int(1)
        else:
            return sv_int(0)
