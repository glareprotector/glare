from features import *




class aggregate_feature(feature):
    """
    abstract class.  requirement is that the only argument to generate is a bucket
    """
    def check_input(self, x):
        import helper
        assert helper.isiterable(x)

# if a feature output is to be used for bucket functions, then it has to implement get_value
class get_bucket_mean_feature(aggregate_feature):
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


class get_bucket_sum_feature(aggregate_feature):
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


class get_bucket_sd_feature(aggregate_feature):
    """
    might raise exception
    """
    def _generate(self, bucket):
        import helper, pdb, basic_features as bf
        mean = bf.always_raise(get_bucket_mean_feature())(bucket)
        bucket_sqr_dist = bf.feature_applier(lambda x: pow(x-mean,2))(bucket)
        avg_sqr_dist = bf.always_raise(get_bucket_mean_feature())(bucket_sqr_dist)
        if abs(avg_sqr_dist) < .0001:
            return 1.0
        return pow(avg_sqr_dist, 0.5)

class get_uncertainty_point_feature(aggregate_feature):
    """
    returns uncertainty_point of bucket.  might raise exception
    """
    def _generate(self, bucket):
        import pdb, basic_features as bf
        mean = bf.always_raise(get_bucket_mean_feature())(bucket)
        width = get_bucket_CI_width_feature()(bucket)
        import my_data_types
        return my_data_types.uncertainty_point.init_normal(mean, mean-width, mean+width)

class get_bucket_CI_width_feature(aggregate_feature):
    def _generate(self, bucket):
        count = get_bucket_count_feature()(bucket)
        sd = get_bucket_sd_feature()(bucket)
        return 1.96 * sd / pow(count, 0.5)


class get_bucket_max_feature(aggregate_feature):

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


class get_bucket_min_feature(aggregate_feature):

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


class get_bucket_count_feature(aggregate_feature):
    """
    returns the number of objects in buckets that are not no_value_objects
    """
    def _generate(self, bucket):
        count = 0
        for item in bucket:
            if not isinstance(item, my_data_types.no_value_object):
                count += 1
        return count


class get_bucket_count_nonzero_feature(aggregate_feature):
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



class get_bucket_label_feature(aggregate_feature):
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

class get_bucket_label_feature_justone(aggregate_feature):

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

