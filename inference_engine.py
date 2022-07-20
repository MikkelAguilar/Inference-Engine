import itertools

SYMBOLS = ['=>', '&', '<=>', '~', '||']

class InferenceEngine:
    def __init__(self):
        self.knowledge_base = []
        self.query = None
        self.propositional_symbols = set()

    def read_from_file(self, filename): #Infer data from the file
        file = open(filename, 'r')
        lines = []
        length_of_file = len(file.readlines())
        file.seek(0)
        
        for i in range(length_of_file):
            lines.append(file.readline().rstrip('\n'))

        index = 0
        for line in lines:
            if line.upper() == 'TELL':
                temp = lines[index + 1].split(";")
                self.knowledge_base = ["".join(x.split()) for x in temp if x != ''] #Set the knowledge base to a list, separated by semicolons in the file
            elif line.upper() == 'ASK':
                self.query = lines[index + 1] #Set the query to the line after the 'ASK'
            index += 1
        

        symbols_to_replace = ['(', ')', '=', '>', '&', '<', '~', '|']
        length_counter = 0

        for clause in self.knowledge_base: #Loop over the clauses and finds all the used propositional symbols
            for symbol in symbols_to_replace: #Replace all the symbols with whitespace
                clause = clause.replace(symbol, ' ')
            for i in range(len(clause)):
                if length_counter > 1: #Skips the iteration if the length of temp is still greater than 1
                    length_counter -= 1
                    continue
                length_counter = 0
                if clause[i] != ' ': #Finds the beginning of the propositional symbol
                    temp = ''
                    for j in range(i, len(clause)):
                        if clause[j] == ' ': #Stops incrementing once whitespace is found
                            break
                        temp += clause[j]
                        length_counter += 1
                    self.propositional_symbols.add(temp) #Add temp to propositional symbols
            
        KB = []
        for sentence in self.knowledge_base: #Loop over the knowledge base and put them to list form
            KB.append(self.separate_sentence(sentence))
        self.knowledge_base = KB

        self.propositional_symbols = list(self.propositional_symbols) #Changes proposition symbols to a list from a set
        self.propositional_symbols.sort()
    
    def separate_sentence(self, sentence): #Given a horn clause, it seperates the items and puts it in list form ||| (a<=>(c=>~d))&b&(b=>a)
        x = []
        index = 0
        t = False
        for i in range(len(sentence)):
            if sentence[i] == '&': #Find the & symbol and seperate the symbols before and after it
                temp = ""
                for j in range(index, i):
                    temp += sentence[j]
                if temp != '':
                    x.append(temp)
                x.append('&')
                index = i + 1
            elif sentence[i] == '=' and sentence[i + 1] == '>': #Find the => symbol and seperate the symbols before and after it
                if t:
                    t = False
                    continue
                temp = ""
                for j in range(index , i):
                    temp += sentence[j]
                if temp != '':
                    x.append(temp)
                x.append('=>')
                index = i + 2
            elif sentence[i] == '<' and sentence[i + 1] == '=' and sentence[i + 2] == '>': #Find the <=> symbol and seperate the symbols before and after it
                temp = ""
                for j in range(index , i):
                    temp += sentence[j]
                if temp != '':
                    x.append(temp)
                x.append('<=>')
                index = i + 3
                t = True
            elif sentence[i] == '|' and sentence[i + 1] == '|': #Find the <=> symbol and seperate the symbols before and after it
                temp = ""
                for j in range(index , i):
                    temp += sentence[j]
                if temp != '':
                    x.append(temp)
                x.append('||')
                index = i + 2
            elif sentence[i] == '(': #Find the <=> symbol and seperate the symbols before and after it
                temp = ""
                for j in range(index , i):
                    temp += sentence[j]
                if temp != '':
                    x.append(temp)
                x.append('(')
                index = i + 1
            elif sentence[i] == ')': #Find the <=> symbol and seperate the symbols before and after it
                temp = ""
                for j in range(index , i):
                    temp += sentence[j]
                if temp != '':
                    x.append(temp)
                x.append(')')
                index = i + 1
            elif sentence[i] == '~': #Find the <=> symbol and seperate the symbols before and after it
                temp = ""
                for j in range(index , i):
                    temp += sentence[j]
                if temp != '':
                    x.append(temp)
                x.append('~')
                index = i + 1
        
        temp = ""
        for i in range(index, len(sentence)):
            temp += sentence[i]
        if temp != '':
            x.append(temp)
        return x
    
    def create_table(self, n): #Use cartesian product create a list of size n, showing all the possible true and false combinations
        table = list(itertools.product([False, True], repeat=n))
        return table
    
    def create_truth_table_dict(self, table): #Using the table from earlier, creates a list of dictionaries where the key is are the symbols and the values is the boolean
        table_dict = []
        for x in table:
            temp_dict = {} #Temporary dictionary
            index = 0
            for value in x:
                temp_dict[self.propositional_symbols[index]] = value #Set a propositional symbol in the current index to a boolean value
                index += 1
            table_dict.append(temp_dict) #Add the dictionary to the list
        return table_dict
    
    def check_statement(self, symbol1, operator, symbol2):
        if operator == '&':
            if symbol1 and symbol2: #If both symbols are true return true, otherwise it is false
                return True
            return False
        elif operator == '=>': #If symbol 1 is true but 2 is not, the statement is false, otherwise it is true
            if symbol1:
                if not symbol2:
                    return False
            return True
        elif operator == '~': #return the opposite of symbol 2
            return not symbol2 
        elif operator == '<=>': #If symbol 1 and 2 are equal the statement is true, otherwise it is false
            if symbol1 == symbol2:
                return True
            return False
        elif operator == '||': #If either symbol 1 or 2 is true the statement is true, otherwise it is false
            if symbol1 or symbol2:
                return True
            return False

    def simplify(self, clause): #Given a clause in list form with symbols replaced as boolean values, simplify the queries until there is only a single boolean left
        valid = [True, False]
        while True:
            for i in range(len(clause)):
                if clause[i] == '(' and clause[i + 2] == ')': #If the list item is an open parethesis, and the third item is a closing parenthesis, it means it can be removed as there is only a single boolean value in there
                    clause.pop(i)
                    clause.pop(i + 1)
                    break
                elif clause[i] == '~': #If the list item is negation, replace the statement with the new value and remove the symbol
                    clause[i + 1] = self.check_statement(clause[i - 1], clause[i], clause[i + 1])
                    clause.pop(i)
                    break
                elif clause[i] == '<=>' and clause[i - 1] in valid and clause[i + 1] in valid: #If the list item is biconditional, replace the statement after the symbol with the new value and remove the propostional and equations symbols
                    clause[i + 1] = self.check_statement(clause[i - 1], clause[i], clause[i + 1])
                    clause.pop(i)
                    clause.pop(i - 1)
                    break
                elif clause[i] == '=>' and clause[i - 1] in valid and clause[i + 1] in valid: #If the list item is conditional, replace the statement after the symbol with the new value and remove the propostional and equations symbols
                    clause[i + 1] = self.check_statement(clause[i - 1], clause[i], clause[i + 1])
                    clause.pop(i)
                    clause.pop(i - 1)
                    break
                elif clause[i] == '&' and clause[i - 1] in valid and clause[i + 1] in valid: #If the list item is 'AND', replace the statement after the symbol with the new value and remove the propostional and equations symbols
                    clause[i + 1] = self.check_statement(clause[i - 1], clause[i], clause[i + 1])
                    clause.pop(i)
                    clause.pop(i - 1)
                    break
                elif clause[i] == '||' and clause[i - 1] in valid and clause[i + 1] in valid: #If the list item is 'OR', replace the statement after the symbol with the new value and remove the propostional and equations symbols
                    clause[i + 1] = self.check_statement(clause[i - 1], clause[i], clause[i + 1])
                    clause.pop(i)
                    clause.pop(i - 1)
                    break
                
            if len(clause) == 1: #Break the loop once the clause is left with a single boolean value
                break
                
        return clause[0] #return the simplified boolean

    def clause_true_in_model(self, model, clause): #Determines whether a clause is true given a dictionary model
        clause_copy = clause.copy() #Create of copy of the clause
        for symbol, value in model.items(): #Loop over the key and values of the model
            for i in range(len(clause_copy)):
                if clause_copy[i] == symbol: #Change the symbols in the clause to either true or false
                    clause_copy[i] = value
        return self.simplify(clause_copy)

    
    def check_head(self, clause): #Given a transformed clause, such as [True, '=>', 'p3'] and [True, '&', True, '=>', 'h'], it returns true if the all the values left to the '=>' symbol is true and false if not
        head = []
        for symbol in clause:
            if symbol == '=>': #Break the loop once it hits this symbol, otherwise keep added to the head
                break
            head.append(symbol)
        
        for symbol in head:
            if symbol != True and symbol not in SYMBOLS: #If one of the symbols is not true and is not a symbol
                return False
        
        return True
        
    def in_tail(self, clause, query): #Finds out whether a query is in the tail of a clause, for example if 'd' was the query, ['p1', '=>', 'd'] would return true
        if clause[-1] == query: #Since the tail is only a single symbol, check if it is equal to the query
            return True
        return False
    
    def is_head_proved(self, clause, proved_statements): #Checks if the head of a horn clause is true given a list of symbols that are true
        head = []
        for symbol in clause:
            if symbol == '=>':
                break
            head.append(symbol)
        
        for symbol in head:
            if symbol not in proved_statements and symbol not in SYMBOLS:
                return False
        
        return True
    
    def get_head_values(self, clause): #Gets all the symbols of the clause head
        head = []
        for symbol in clause:
            if symbol == '=>':
                break
            if symbol not in SYMBOLS:
                head.append(symbol)
        
        return head
    
    def remove_duplicates(self, list): #A function to remove any duplicate values in a list
        res = []
        [res.append(x) for x in list if x not in res]

        return res
    
    def truth_table_checking(self, query): #Truth Table Checking
        table_dictionary = self.create_truth_table_dict(self.create_table(len(self.propositional_symbols)))
        valid_models = [] #Models where the KB is true
        query = self.separate_sentence(query) #Change query to a list form
        number_models_entail_query = 0

        for model in table_dictionary: 
            KB = True
            for clause in self.knowledge_base: #Loops over the clauses and checks if all clauses are true in the model, if not it breaks the loop, sets KB to false
                if not self.clause_true_in_model(model, clause):
                    KB = False
                    break
            if KB: #If KB is not false it adds 1 to number of valid models that may entail the query
                valid_models.append(model)
        
        for valid_model in valid_models: #Checks all valid models and if the query is true in that model, increment the number of models that entail the query
            if self.clause_true_in_model(valid_model, query):
                number_models_entail_query += 1
        
        if number_models_entail_query > 0: #If the number of models is greater than 0 return Yes and the number of models, otherwise return
            return 'YES: ' + str(number_models_entail_query)
        return 'NO: "' + str(self.query) + '" is not entailed in any of the models'
    
    def forward_chaining(self, query):
        KB = self.knowledge_base.copy() #Create a copy of the knowledge base
        symbols_entailed = []

        for clause in KB: #Appends all single horn clause statements to symbols entailed
            if len(clause) == 1:
                symbols_entailed.append(clause[0])

        KB = [x for x in KB if len(x) > 1] #Removes all the clauses in KB there are not greater than 1

        while query not in symbols_entailed: #Until the query is in symbols entailed
            valid_query = False
            for i in range(len(KB)): #If a symbol in a clause is in symbols entailed, set it to true
                for j in range(len(KB[i])):
                    if KB[i][j] in symbols_entailed:
                        KB[i][j] = True
            
            for clause in KB: #Loop through the clauses and check if the head is true, if it is add the tail to the symbols entailed, remove the clause from KB and set it to valid
                if (self.check_head(clause)):
                    symbols_entailed.append(clause[-1])
                    KB.remove(clause)
                    valid_query = True
            
            if not valid_query: #If none of the clauses have a head that is true, return no
                return 'NO'
        
        string = ", ".join(symbols_entailed)
        return "YES: " + string #returns yes with the all the symbols entailed separated with a comma
    
    def backward_chaining(self, query):
        KB = self.knowledge_base.copy()
        current_prove = [query] #Keeps a list symbols that have not need to, but have not been proved yet
        visited = []
        proved_statements = [] #List of proved symbols
        valid = False
        next_cp = []

        for clause in KB: #Appends all single horn clause statements to proved statements
            if len(clause) == 1:
                proved_statements.append(clause[0])
        
        while True:
            for cp in current_prove:
                for clause in KB:
                    if self.in_tail(clause, cp): 
                        valid = True
                        if self.is_head_proved(clause, proved_statements): #If the head is proved add the current prove and the head values to visited
                            visited.extend(current_prove)
                            visited.extend(self.get_head_values(clause))
                            x = self.remove_duplicates(visited)
                            x.reverse() #Reverse the list
                            string = ", ".join(x)
                            return "YES: " + string 
                        else: #If the head is not yet proved, add the current prove to visited and the head values to the next current prove
                            visited.extend(current_prove)
                            next_cp.extend(self.get_head_values(clause))
                            visited.extend([x for x in next_cp if x in proved_statements]) #Add the next current prove to visited if not arleady proved
                            next_cp = [x for x in next_cp if x not in proved_statements] #Remove the already proved symbols from the next CP
            if valid == False: #If after looping all the clauses in KB and the current proves there is no next clause to analyse, return a 'NO'
                return "NO"

            current_prove = next_cp
            next_cp = []
            valid = False
    
    def search_stats(self, method): #Performs a method of checking and returns the value given an acronym of the method
        if method.upper() == 'TTC':
            x = self.truth_table_checking(self.query)
        elif method.upper() == 'FC':
            x = self.forward_chaining(self.query)
        elif method.upper() == 'BC':
            x = self.backward_chaining(self.query)
        
        return x

if __name__ == '__main__':
    engine = InferenceEngine()
    engine.read_from_file('test_genericKB.txt') #test_genericKB.txt #test_HornKB.txt