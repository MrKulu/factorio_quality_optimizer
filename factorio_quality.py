from decimal import Decimal, getcontext
import itertools
import csv

# decimal precision
getcontext().prec = 20

# k: maximum number of modules
# p5: productivity bonus of one module
# returns the expected number of Q5 output from one Q5 input
def h5(k, p5):
    # when using Q5 input, it is best to use only productivity modules, since the output is guaranteed to be Q5
    return 1 + (p5*k)

# k: maximum number of modules
# p4: productivity bonus of one module
# q4: quality bonus of one module
# h5: optimized value of 5th assembly machine
# qr: total quality bonus on recyclers
# returns the best expected number of Q5 output from one Q4 input, with the associated number of productivity and quality modules
def h4(k, p4, q4, h5, qr):
    # possible combinations of productivity and quality modules (min one quality module)
    comb = [(p4*i,q4*(k-i),i,(k-i)) for i in range(k)]
    r = []
    for (p, q, n_p, n_q) in comb:
        # productivity factor
        p = 1 + p
        div = (4 / (p * (1 - q) * (1 - qr))) - 1
        coeff5 = qr / (1 - qr)
        const = 4 * q / ((1 - q) * (1 - qr))
        
        h = (coeff5 * h5 + const) / div

        r.append((h, n_p, n_q))

    r.sort(key=lambda x: x[0], reverse=True)
    return r[0]

# The other functions are very similar to h4...

def h3(k, p3, q3, h5, h4, qr):
    comb = [(p3*i,q3*(k-i),i,(k-i)) for i in range(k)]
    r = []
    for (p, q, n_p, n_q) in comb:
        p = 1 + p
        # div is always the same
        div = (4 / (p * (1 - q) * (1 - qr))) - 1
        coeff4 = (q + qr)
        coeff5 = (qr / (1 - qr)) * coeff4
        const = 4 * (q ** 2) / ((1 - q) * (1 - qr))
        
        h = (coeff4 * h4 + coeff5 * h5 + const) / div

        r.append((h, n_p, n_q))

    r.sort(key=lambda x: x[0], reverse=True)
    return r[0]

def h2(k, p2, q2, h5, h4, h3, qr):
    comb = [(p2*i,q2*(k-i),i,(k-i)) for i in range(k)]
    r = []
    for (p, q, n_p, n_q) in comb:
        p = 1 + p
        div = (4 / (p * (1 - q) * (1 - qr))) - 1
        coeff3 = (q + qr)
        coeff4 = ((q ** 2) + (q * qr) + (qr ** 2))
        coeff5 = (qr / (1 - qr)) * coeff4
        const = 4 * (q ** 3) / ((1 - q) * (1 - qr))
        
        h = (coeff3 * h3 + coeff4 * h4 + coeff5 * h5 + const) / div

        r.append((h, n_p, n_q))

    r.sort(key=lambda x: x[0], reverse=True)
    return r[0]

def h1(k, p1, q1, h5, h4, h3, h2, qr):
    comb = [(p1*i,q1*(k-i),i,(k-i)) for i in range(k)]
    r = []
    for (p, q, n_p, n_q) in comb:
        p = 1 + p
        div = (4 / (p * (1 - q) * (1 - qr))) - 1
        coeff2 = (q + qr)
        coeff3 = ((q ** 2) + (q * qr) + (qr ** 2))
        coeff4 = ((q ** 3) + (q ** 2) * qr + q * (qr ** 2) + (qr ** 3))
        coeff5 = (qr / (1 - qr)) * coeff4
        const = 4 * (q ** 4) / ((1 - q) * (1 - qr))
        
        h = (coeff2 * h2 + coeff3 * h3 + coeff4 * h4 + coeff5 * h5 + const) / div

        r.append((h, n_p, n_q))

    r.sort(key=lambda x: x[0], reverse=True)
    return r[0]

prod_modules = {"T1Q1": Decimal('0.04'), "T1Q2": Decimal('0.05'), "T1Q3": Decimal('0.06'), "T1Q4": Decimal('0.07'), "T1Q5": Decimal('0.10'),
                "T2Q1": Decimal('0.06'), "T2Q2": Decimal('0.07'), "T2Q3": Decimal('0.09'), "T2Q4": Decimal('0.11'), "T2Q5": Decimal('0.15'),
                "T3Q1": Decimal('0.10'), "T3Q2": Decimal('0.13'), "T3Q3": Decimal('0.16'), "T3Q4": Decimal('0.19'), "T3Q5": Decimal('0.25')}
    
qual_modules = {"T1Q1": Decimal('0.010'), "T1Q2": Decimal('0.013'), "T1Q3": Decimal('0.016'), "T1Q4": Decimal('0.019'), "T1Q5": Decimal('0.025'),
                "T2Q1": Decimal('0.020'), "T2Q2": Decimal('0.026'), "T2Q3": Decimal('0.032'), "T2Q4": Decimal('0.038'), "T2Q5": Decimal('0.050'),
                "T3Q1": Decimal('0.025'), "T3Q2": Decimal('0.032'), "T3Q3": Decimal('0.040'), "T3Q4": Decimal('0.047'), "T3Q5": Decimal('0.062')}

def get_module_kind(tier, quality):
    return "T" + str(tier) + "Q" + str(quality)

def get_all_modules_under(tier, quality):
    return [get_module_kind(t, q) for t in range(1, tier+1) for q in range(1, quality+1)]

def save_to_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def save_intermediate_results(r,filename):
    headers = ["Productivity module", "Prod bonus", "Quality module", "Qual bonus", "E_out", "n_p", "n_q"]
    csv_data = [headers] + r
    save_to_csv(csv_data, filename)
    print("CSV file saved as " + filename)

# combinations: list of tuples (p, q) where p is the productivity module and q is the quality module
# All combinations are tested for each machine, and the best result is kept for the next machine.
# We can solve from the highest quality producing machine to the lowest. (see the definitions of the h_i)
# Since each h_i is optimized, this also means that the setup can take any quality of outside input (not just Q1), and still be optimal.
def aux(k, max_tier, max_quality, combinations, file_suffix):
    # 4 quality modules per recycler
    qr = qual_modules[get_module_kind(max_tier, max_quality)] * 4
    # best productivity module in max tier assembly machine
    p5 = prod_modules[get_module_kind(max_tier, max_quality)]
    h5_value = h5(k, p5)
    print("Q5 expected output: " + str(h5_value))
    # best h4 value
    r = []
    for (p, q) in combinations:
        p4 = prod_modules[p]
        q4 = qual_modules[q]
        r.append((p, p4, q, q4, *h4(k, p4, q4, h5_value, qr)))

    filename_h4 = 'h4_'+str(k)+'_'+file_suffix+'.csv'
    save_intermediate_results(r, filename_h4)

    r.sort(key=lambda x: x[4], reverse=True)
    print("Q4 expected output: " + str(r[0][4]) + " P:" + str(r[0][5]) + " Q:" + str(r[0][6]))
    h4_value = r[0][4]

    # best h3 value
    r = []
    for (p, q) in combinations:
        p3 = prod_modules[p]
        q3 = qual_modules[q]
        r.append((p, p3, q, q3, *h3(k, p3, q3, h5_value, h4_value, qr)))

    filename_h3 = 'h3_'+str(k)+'_'+file_suffix+'.csv'
    save_intermediate_results(r, filename_h3)

    r.sort(key=lambda x: x[4], reverse=True)
    print("Q3 expected output: " + str(r[0][4]) + " P:" + str(r[0][5]) + " Q:" + str(r[0][6]))
    h3_value = r[0][4]

    # best h2 value
    r = []
    for (p, q) in combinations:
        p2 = prod_modules[p]
        q2 = qual_modules[q]
        r.append((p, p2, q, q2, *h2(k, p2, q2, h5_value, h4_value, h3_value, qr)))

    filename_h2 = 'h2_'+str(k)+'_'+file_suffix+'.csv'
    save_intermediate_results(r, filename_h2)

    r.sort(key=lambda x: x[4], reverse=True)
    print("Q2 expected output: " + str(r[0][4]) + " P:" + str(r[0][5]) + " Q:" + str(r[0][6]))
    h2_value = r[0][4]

    # best h1 value
    r = []
    for (p, q) in combinations:
        p1 = prod_modules[p]
        q1 = qual_modules[q]
        r.append((p, p1, q, q1, *h1(k, p1, q1, h5_value, h4_value, h3_value, h2_value, qr)))

    filename_h1 = 'h1_'+str(k)+'_'+file_suffix+'.csv'
    save_intermediate_results(r, filename_h1)

    r.sort(key=lambda x: x[4], reverse=True)
    print("Q1 expected output: " + str(r[0][4]) + " P:" + str(r[0][5]) + " Q:" + str(r[0][6]))
    # h1_value = r[0][4] (unused)

# All possible combinations of tier and qualities for modules
def main_full(k, max_tier, max_quality):
    module_kinds = get_all_modules_under(max_tier, max_quality)
    all_combinations = list(itertools.product(module_kinds, repeat=2))
    aux(k, max_tier, max_quality, all_combinations, "full_t"+str(max_tier)+"q"+str(max_quality))

# Productivity and Quality modules have the same tier and quality
def main_same(k, max_tier, max_quality):
    module_kinds = get_all_modules_under(max_tier, max_quality)
    combinations = [(x,x) for x in module_kinds]
    aux(k, max_tier, max_quality, combinations, "same_t"+str(max_tier)+"q"+str(max_quality))

# Using max_tier=3, max_quality=5 assumes everything has been unlocked.
# Using max_tier=2, max_quality=3 for early game of quality setup.
# If higher qualities haven't been unlocked yet, the results can translate: for instance, if Rare (Q3) is the highest quality available, use the result
# for h3 for Q1 machines (i.e, h5 is always the highest quality machine available).
if __name__ == "__main__":
    # main_full(4,3,5)
    main_same(4,3,5)
    # main_full(2,3,5)
    # main_same(2,3,5)
    # main_full(4,2,3)
    main_same(4,2,3)
    # main_full(2,2,3)
    # main_same(2,2,3)
