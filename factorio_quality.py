from decimal import Decimal, getcontext
import itertools
import csv

# decimal precision
getcontext().prec = 20

# k: maximum number of modules
# p5: productivity bonus of one module
# bp: base productivity of the machine
# returns the expected number of Q5 output from one Q5 input
def h5(k, p5, bp):
    # when using Q5 input, it is best to use only productivity modules, since the output is guaranteed to be Q5
    return (bp + (p5*k),k,0)

# k: maximum number of modules
# p4: productivity bonus of one module
# q4: quality bonus of one module
# h5: optimized value of 5th assembly machine
# qr: total quality bonus on recyclers
# bp: base productivity of the machine
# returns the best expected number of Q5 output from one Q4 input, with the associated number of productivity and quality modules
def h4(k, p4, q4, h5, qr, bp):
    # possible combinations of productivity and quality modules (min one quality module)
    comb = [(p4*i,q4*(k-i),i,(k-i)) for i in range(k)]
    r = []
    for (p, q, n_p, n_q) in comb:
        # productivity factor
        p = bp + p
        div = (4 / p) - ((1 - q) * (1 - qr))
        coeff5 = qr * (1 - q)
        const = 4 * q
        
        h = (coeff5 * h5 + const) / div

        r.append((h, n_p, n_q))

    r.sort(key=lambda x: x[0], reverse=True)
    return r[0]

# The other functions are very similar to h4...

def h3(k, p3, q3, h5, h4, qr, bp):
    comb = [(p3*i,q3*(k-i),i,(k-i)) for i in range(k)]
    r = []
    for (p, q, n_p, n_q) in comb:
        p = bp + p
        # div is always the same
        div = (4 / p) - ((1 - q) * (1 - qr))
        coeff4 = Decimal('0.9') * ((1 - q) * qr + (1 - qr) * q)
        coeff5 = qr * ((1 - q) * Decimal('0.1') + q * Decimal('0.9'))
        const = 4 * q * Decimal('0.1')
        
        h = (coeff4 * h4 + coeff5 * h5 + const) / div

        r.append((h, n_p, n_q))

    r.sort(key=lambda x: x[0], reverse=True)
    return r[0]

def h2(k, p2, q2, h5, h4, h3, qr, bp):
    comb = [(p2*i,q2*(k-i),i,(k-i)) for i in range(k)]
    r = []
    for (p, q, n_p, n_q) in comb:
        p = bp + p
        div = (4 / p) - ((1 - q) * (1 - qr))
        coeff3 = Decimal('0.9') * ((qr * (1 - q)) + q * (1 - qr))
        coeff4 = ( ((1-q)*qr* Decimal('0.09')) + (q * qr * Decimal('0.9') * Decimal('0.9')) + (q * (1-qr) * Decimal('0.09'))  )
        coeff5 =  ( ((1-q)*qr* Decimal('0.01')) + (q * qr * Decimal('0.9') * Decimal('0.1')) + (q * qr * Decimal('0.09'))  )
        const = 4 * q * Decimal('0.01')
        
        h = (coeff3 * h3 + coeff4 * h4 + coeff5 * h5 + const) / div

        r.append((h, n_p, n_q))

    r.sort(key=lambda x: x[0], reverse=True)
    return r[0]

def h1(k, p1, q1, h5, h4, h3, h2, qr, bp):
    comb = [(p1*i,q1*(k-i),i,(k-i)) for i in range(k)]
    r = []
    for (p, q, n_p, n_q) in comb:
        p = bp + p
        div = (4 / p) - ((1 - q) * (1 - qr))
        coeff2 = Decimal('0.9') * ((qr * (1 - q)) + q * (1 - qr))
        coeff3 = ( ((1-q)*qr* Decimal('0.09')) + (q * qr * Decimal('0.9') * Decimal('0.9')) + (q * (1-qr) * Decimal('0.09'))  )
        coeff4 = ( ((1-q)*qr* Decimal('0.009')) + 2 * (q * qr * Decimal('0.09') * Decimal('0.9')) + (q * (1-qr) * Decimal('0.009'))  )
        coeff5 = ( ((1-q)*qr* Decimal('0.001')) + 2 * (q * qr * Decimal('0.09') * Decimal('0.1')) + (q * qr * Decimal('0.009'))  )
        const =  4 * q * Decimal('0.001')
        
        h = (coeff2 * h2 + coeff3 * h3 + coeff4 * h4 + coeff5 * h5 + const) / div

        r.append((h, n_p, n_q))

    r.sort(key=lambda x: x[0], reverse=True)
    return r[0]

prod_modules = {"T0Q0": Decimal('0'), # When the recipe does not accept productivity modules
                "T1Q1": Decimal('0.04'), "T1Q2": Decimal('0.05'), "T1Q3": Decimal('0.06'), "T1Q4": Decimal('0.07'), "T1Q5": Decimal('0.10'),
                "T2Q1": Decimal('0.06'), "T2Q2": Decimal('0.07'), "T2Q3": Decimal('0.09'), "T2Q4": Decimal('0.11'), "T2Q5": Decimal('0.15'),
                "T3Q1": Decimal('0.10'), "T3Q2": Decimal('0.13'), "T3Q3": Decimal('0.16'), "T3Q4": Decimal('0.19'), "T3Q5": Decimal('0.25')}
    
qual_modules = {"T1Q1": Decimal('0.010'), "T1Q2": Decimal('0.013'), "T1Q3": Decimal('0.016'), "T1Q4": Decimal('0.019'), "T1Q5": Decimal('0.025'),
                "T2Q1": Decimal('0.020'), "T2Q2": Decimal('0.026'), "T2Q3": Decimal('0.032'), "T2Q4": Decimal('0.038'), "T2Q5": Decimal('0.050'),
                "T3Q1": Decimal('0.025'), "T3Q2": Decimal('0.032'), "T3Q3": Decimal('0.040'), "T3Q4": Decimal('0.047'), "T3Q5": Decimal('0.062')}


def save_to_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# We can solve from the highest quality producing machine to the lowest. (see the definitions of the h_i)
# Note: Since each h_i is optimized, this also means that the setup can take any quality of outside input (not just Q1), and still be optimal.
def full_setup(k, best_prod, best_quality, bp):
    # p: max avialable quality for productivity modules
    # q: max available quality for quality modules
    # It is always better to use the best available modules.
    p = prod_modules[best_prod];
    q = qual_modules[best_quality];
    # 4 quality modules per recycler
    qr = q * 4
    # best productivity module in max tier assembly machine
    p5 = p
    h5_value = h5(k, p5, bp)
    # best h4 value
    h4_value = h4(k, p, q, h5_value[0], qr, bp)
    # best h3 value
    h3_value = h3(k, p, q, h5_value[0], h4_value[0], qr, bp)
    # best h2 value
    h2_value = h2(k, p, q, h5_value[0], h4_value[0], h3_value[0], qr, bp)
    # best h1 value
    h1_value = h1(k, p, q, h5_value[0], h4_value[0], h3_value[0], h2_value[0], qr, bp)
    return (h1_value, h2_value, h3_value, h4_value, h5_value)

def format_solution(sol):
    (h1, h2, h3, h4, h5) = sol
    def aux(h):
        return "[P:%s Q:%s] | E_out:%s" % (str(h[1]), str(h[2]), str(h[0]))
    return "\n".join([aux(h1), aux(h2), aux(h3), aux(h4), aux(h5)])

# All possible combinations of tier and qualities for modules, and save it to a csv file
def main(k, bp, file_suffix):
    prod_keys = prod_modules.keys()
    qual_keys = qual_modules.keys()
    d = {}
    for pk in prod_keys:
        for qk in qual_keys:
            d[(pk, qk)] = full_setup(k, pk, qk, bp)
    header = ["Prod\\Qual"] + list(qual_keys)
    r = []
    for pk in prod_keys:
        row = [pk]
        for qk in qual_keys:
            row.append(format_solution(d[(pk, qk)]))
        r.append(row)
    r.insert(0, header)
    save_to_csv(r, "results_" + file_suffix + ".csv")

# If higher qualities haven't been unlocked yet, the results can translate: for instance, if Rare (Q3) is the highest quality available, use the result
# for h3 for Q1 machines (i.e, h5 is always the highest quality machine available).
if __name__ == "__main__":
    # Assembly machine 1 and 2
    main(2, Decimal('1'), "a2")
    # Assembly machine 3
    main(4, Decimal('1'), "a3")
    # Electromagnetic plant
    main(5, Decimal('1.5'), "ep")

