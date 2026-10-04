import pandas as pd
import sys
import os

def parse_boolean(val):
    v = val.strip().lower()
    if v == 'true':
        return True
    elif v == 'false':
        return False
    return None

def score_validation():
    if not os.path.exists('output/my_answers.txt'):
        print("output/my_answers.txt not found.")
        return
        
    if not os.path.exists('output/validation_key.csv'):
        print("output/validation_key.csv not found.")
        return
        
    key_df = pd.read_csv('output/validation_key.csv')
    
    with open('output/my_answers.txt', 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
        
    my_answers = {}
    malformed = []
    
    for line_idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        parts = line.split(',')
        if len(parts) != 3:
            malformed.append((line_idx + 1, line))
            continue
            
        tid = parts[0].strip()
        shift = parts[1].strip().capitalize()
        breach = parse_boolean(parts[2])
        
        if breach is None:
            malformed.append((line_idx + 1, line))
            continue
            
        my_answers[tid] = {'shift': shift, 'breach': breach}
        
    if malformed:
        print("Malformed lines found:")
        for idx, line in malformed:
            print(f"Line {idx}: {line}")
        return
        
    key_tids = set(key_df['ticket_id'])
    my_tids = set(my_answers.keys())
    
    missing = key_tids - my_tids
    extra = my_tids - key_tids
    
    if missing or extra:
        if extra:
            print("Tickets in your file not in the sample:", extra)
        if missing:
            print("Sample tickets you did not answer:", missing)
        print("Please fix output/my_answers.txt to match the sample exactly.")
        return
        
    # Score
    total = len(key_df)
    shift_correct = 0
    breach_correct = 0
    mismatches = []
    
    # For case_type breakdown
    case_type_stats = {}
    for ct in key_df['case_type'].unique():
        case_type_stats[ct] = {'total': 0, 'shift_correct': 0, 'breach_correct': 0}
        
    for _, row in key_df.iterrows():
        tid = row['ticket_id']
        t_shift = row['tool_shift_ist']
        t_breach = row['tool_breach']
        ct = row['case_type']
        
        m_shift = my_answers[tid]['shift']
        m_breach = my_answers[tid]['breach']
        
        s_ok = m_shift == t_shift
        b_ok = m_breach == t_breach
        
        case_type_stats[ct]['total'] += 1
        if s_ok:
            shift_correct += 1
            case_type_stats[ct]['shift_correct'] += 1
        if b_ok:
            breach_correct += 1
            case_type_stats[ct]['breach_correct'] += 1
            
        if not s_ok or not b_ok:
            mismatches.append({
                'ticket_id': tid,
                'case_type': ct,
                'tool_shift': t_shift, 'my_shift': m_shift,
                'tool_breach': t_breach, 'my_breach': m_breach
            })
            
    shift_err_rate = (total - shift_correct) / total * 100
    breach_err_rate = (total - breach_correct) / total * 100
    
    print(f"Sample size: {total}")
    print(f"Correct shift: {shift_correct}/{total} (Error rate: {shift_err_rate:.1f}%)")
    print(f"Correct breach: {breach_correct}/{total} (Error rate: {breach_err_rate:.1f}%)")
    
    print("\nBreakdown by case_type:")
    for ct, stats in case_type_stats.items():
        n = stats['total']
        sc = stats['shift_correct']
        bc = stats['breach_correct']
        print(f"  {ct} (n={n}): shift {sc}/{n}, breach {bc}/{n}")
        
    if mismatches:
        print("\nMismatches:")
        for m in mismatches:
            print(f"Ticket: {m['ticket_id']} ({m['case_type']})")
            if m['tool_shift'] != m['my_shift']:
                print(f"  Shift mismatch: tool={m['tool_shift']}, yours={m['my_shift']}")
            if m['tool_breach'] != m['my_breach']:
                print(f"  Breach mismatch: tool={m['tool_breach']}, yours={m['my_breach']}")
    else:
        bound = 3 / total * 100
        print(f"\nZero errors found. Rule of 3 (95% upper bound for error rate): {bound:.1f}%.")
        print(f"This means we are 95% confident the true error rate in the population is below {bound:.1f}%.")
        
    # Write summary
    os.makedirs('docs', exist_ok=True)
    with open('docs/validation_results.md', 'w') as f:
        f.write("# Validation Results\n\n")
        f.write(f"- Sample size: {total}\n")
        f.write(f"- Shift accuracy: {shift_correct}/{total} (Error rate: {shift_err_rate:.1f}%)\n")
        f.write(f"- Breach accuracy: {breach_correct}/{total} (Error rate: {breach_err_rate:.1f}%)\n")
        if not mismatches:
            bound = 3 / total * 100
            f.write(f"- Zero errors found. 95% upper bound (Rule of 3): {bound:.1f}%.\n")
        else:
            f.write("- Mismatches were found. See console output for details.\n")
            
if __name__ == '__main__':
    score_validation()
