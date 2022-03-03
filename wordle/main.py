WORD_LEN = 5


def load_words(file_name):
    with open(file_name, 'r') as f:
        lines = [line.rstrip() for line in f]
    return lines


def check_word_len(word):
    if len(word) != WORD_LEN:
        raise Exception('Word len is not 5: [{0}]'.format(word))


def check(real, guess):
    result = ['X'] * WORD_LEN
    real_ct = {}
    for i in range(WORD_LEN):
        if real[i] == guess[i]:
            result[i] = 'G'
        else:
            real_ct[real[i]] = real_ct.get(real[i], 0) + 1

    for i in range(WORD_LEN):
        if result[i] != 'X':
            continue
        if real_ct.get(guess[i], 0) > 0:
            result[i] = 'Y'
            real_ct[guess[i]] -= 1
        else:
            result[i] = 'B'
    return ''.join(result)


def calculate_elimination(guess, candidates):
    results_ct = {}
    results = {}
    max_ct = 0
    for candidate in candidates:
        check_result = check(candidate, guess)
        results_ct[check_result] = results_ct.get(check_result, 0) + 1
        if not results.get(check_result):
            results[check_result] = []
        results[check_result].append(candidate)
        max_ct = max(max_ct, results_ct[check_result])
    return max_ct, results


def find_next_guess(guess_candidates, candidates):
    min_max = 1000000
    min_max_candidate = None
    min_max_nxt = None
    for guess_candidate in guess_candidates:
        mx, nxt = calculate_elimination(guess_candidate, candidates)
        if mx < min_max:
            min_max = mx
            min_max_candidate = guess_candidate
            min_max_nxt = nxt
    return min_max_candidate, min_max_nxt


def main():
    candidates_original = load_words('./official_wordle_all.txt')
    candidates = load_words('./official_wordle_all.txt')
    print('Wordle Solve by Steven Sun\n')
    
    itr = 1
    while len(candidates) > 1:
        print(f'Iteration {itr}: =======')
        guess_candidates = candidates_original
        if itr == 1:
            guess_candidates = ['soare']
        candidate, nxt = find_next_guess(guess_candidates, candidates)

        print(f'Please guess [{candidate}]')
        guess_result = input("Enter guess result:")
        guess_result = guess_result.upper()
        candidates = nxt[guess_result]
        print(f'Sure, there are [{len(candidates)}] candidates left')
        if len(candidates) < 10:
            print('Candidates are:')
            print(candidates)
        print('=======\n')
        itr += 1

    if len(candidates) == 1:
        print(f'I know the word, it is [{candidates[0]}]')
    else:
        print(f'No word left in my dictionary. Sorry')
    print('\n\n')


if __name__ == "__main__":
  main()
