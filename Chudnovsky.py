import multiprocessing as mp
import time
import gmpy2


class PQR:

    def __init__(self):
        self.P = None
        self.Q = None
        self.R = None


def add_PQR(pqr1: PQR, pqr2: PQR):
    pqr = PQR()
    pqr.P = pqr1.P * pqr2.P
    pqr.Q = pqr1.Q * pqr2.Q
    pqr.R = pqr1.R * pqr2.Q + pqr1.P * pqr2.R
    return pqr


def set_cpu_core(CORE, N):
    core = CORE
    if CORE is None or CORE < 1:
        core = int(mp.cpu_count())
        print(f"core set to cpu count max: {core}")
    if core > N:
        core = N
        print(f"core set to task max: {core}")
    if core & (core - 1) != 0:
        core = core
        count = -1
        while core != 0:
            core >>= 1
            count += 1
        core = 1 << count
        print(f"core set to 2^n: {core}")
    return core


class Chudnovsky:

    def __init__(self, digits, core=None):
        self.DIGITS = int(digits)
        self.A = gmpy2.mpz(13591409)
        self.B = gmpy2.mpz(545140134)
        C = gmpy2.mpz(640320)
        D = gmpy2.mpz(53360)
        DIGITS_PER_TERM = gmpy2.log(D**3) / gmpy2.log(10)
        self.C3_24 = gmpy2.mpz(C**3 / 24)
        self.N = int(self.DIGITS / DIGITS_PER_TERM)
        self.PREC = int(self.DIGITS * gmpy2.log2(10))
        self.CORE = set_cpu_core(core, self.N)

    def dfs(self, a, b):    #C1,C2
        pqr = PQR()
        if a + 1 == b:
            # pqr.P = 2 * b - 1
            # pqr.P *= 6 * b - 1
            # pqr.P *= 6 * b - 5
            # pqr.P = (6 * b - 5) * (2 * b - 1) * (6 * b - 1)
            pqr.P = gmpy2.mpz((6 * b - 5) * (2 * b - 1) * (6 * b - 1))
            pqr.Q = self.C3_24 * b**3
            pqr.R = gmpy2.mpz((-1) ** b * (self.A + self.B * b) * pqr.P)
        else:
            m = (a + b) // 2
            pqr1 = self.dfs(a, m)
            pqr2 = self.dfs(m, b)
            pqr.P = pqr1.P * pqr2.P
            pqr.Q = pqr1.Q * pqr2.Q
            pqr.R = pqr1.R * pqr2.Q + pqr1.P * pqr2.R
        return pqr

    def task_dfs(self, a, b):
        with mp.Pool(self.CORE) as pool:
            t = time.time()
            param_list = []
            size = int(b / self.CORE)
            start = -size + a
            for i in range(0, self.CORE):
                start += size
                param_list.append((start, start + size))
            param_list[-1] = (start, b)
            res_a = [pool.apply_async(self.dfs, args=(*p,)) for p in param_list]
            task_len = len(res_a)
            print(f"{task_len} compute tasks running......")
            res = [p.get() for p in res_a]
            print(time.time() - t)
        while task_len > 1:
            t = time.time()
            child_res = []
            with mp.Pool(int(task_len / 2)) as pool:
                print(f"{int(task_len / 2)} merge tasks running......")
                for i in range(0, task_len, 2):
                    child_res.append(
                        pool.apply_async(add_PQR, args=(res[i], res[i + 1]))
                    )
                res = [p.get() for p in child_res]
            task_len = len(res)
            print(time.time() - t)
        return res[0]

    def run(self):
        print(f"====== PI ( {str(self.DIGITS)} digits )  Core: {self.CORE} ======")
        t0 = time.time()
        if self.CORE > 1:
            pqr = self.task_dfs(0, self.N)
        else:
            pqr = self.dfs(0, self.N)
        gmpy2.get_context().precision = self.PREC
        pi = 426880 * gmpy2.sqrt(gmpy2.mpfr(10005)) * pqr.Q
        pi /= self.A * pqr.Q + pqr.R
        print(f"Time (compute):{time.time() - t0}")
        t1 = time.time()
        pi_str = str(pi)
        with open("pi.txt", "w") as f:
            f.write(pi_str)
        print(f"Time (write):{time.time() - t1}")
        print(f"Last 100 digits:\n{pi_str[-100:]}")
        print(f"Length: {len(pi_str)}")


if __name__ == "__main__":
    dig = 1e7
    Chudnovsky(dig).run()
    t0 = time.time()
    import mpmath
    mpmath.mp.dps = dig
    pi_str = str(mpmath.pi)
    print(f"====== mpmath ======")
    print(f"TIME (COMPUTE):{time.time() - t0}")
    print(f"Last 100 digits:\n{pi_str[-100:]}")
    print(f"Length: {len(pi_str)}")
