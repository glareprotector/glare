class question(object):

    def __init__(self, name, display_str, allowed_values):
        self.name = name
        self.display_str = display_str
        self.allowed_values = allowed_values

    def __hsh__(self):
        return self.name

    def get_user_answer(self):
        """
        assume that answer will be a integer
        """
        while 1:
            ans = int(raw_input(self.display_str))
            if ans in self.allowed_values:
                break
            
        return ans

bowel_urgency = question('bowel_urgency', 'how often do you have urgency? 1:not at all, 2:rarely, 3:sometimes, 4:everyday', [0,1,2,3,4])

urinary_incontinence = question('urinary_incontinence', 'how often do you leak? 1:never, 2:occassionally, 3:frequent, 4:always', [0,1,2,3,4])





