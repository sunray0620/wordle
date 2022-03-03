from datetime import datetime
import csv
import re
import typing

raw_nba_data_file_path = './nba_raw.csv'
nba_data_file_path = './nba.csv'
nba_team_abbr_file_path = './nba_team_abbr.csv'
nba_team_div_file_path = './nba_team_div.csv'

today_date = '2022-03-02'

class Player:
  def __init__(self) -> None:
    self.last_name = ''
    self.first_name = ''
    self.team = ''
    self.team_div = ''
    self.team_conf = ''
    self.position = ''
    self.number = ''
    self.number_int = ''
    self.height = ''
    self.height_in = 0
    self.height_cm = 0
    self.weight = ''
    self.weight_lb = 0
    self.weight_kg = 0
    self.dob = ''
    self.age = 0

  def populate_position(self) -> None:
    self.position = self.position.replace('/', '')
    self.position = ''.join(sorted(self.position))

  def populate_weight(self) -> None:
    m = re.match(r'(\d+).*\((\d+).*\)', self.weight)
    self.weight_lb = int(m.group(1))
    self.weight_kg = int(m.group(2))

  def populate_height(self) -> None:
    m = re.match(r'(\d+).ft.(\d+).in.\((.*).m\)', self.height)
    self.height_in = int(m.group(1)) * 12 + int(m.group(2))
    self.height_cm = int(m.group(3).replace('.', ''))
  
  def populate_age(self) -> None:
    m = re.match(r'(\d+).(\d+).(\d+)', self.dob)
    year = int(m.group(1))
    month = int(m.group(2))
    date = int(m.group(3))
    dob = datetime(year=year, month=month, day=date)
    today = datetime.strptime(today_date, '%Y-%m-%d')
    self.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

  def populate_number(self) -> None:
    try:
      self.number_int = int(self.number)
    except ValueError:
      self.number_int = -1

  def populate(self) -> None:
    self.populate_position()
    self.populate_weight()
    self.populate_height()
    self.populate_age()
    self.populate_number()

  def __str__(self) -> str:
    ret = ''
    ret += f'Name: {self.first_name} {self.last_name}\n'
    ret += f'DOB: {self.dob} (Age: {self.age})\n'
    ret += f'Team: {self.team} ({self.team_div}/{self.team_conf})\n'
    ret += f'Position: {self.position}\n'
    ret += f'Number: {self.number}\n'
    ret += f'Height: {self.height_in // 12}-{self.height_in % 12} ({self.height_cm} cm) [RAW: {self.height}]\n'
    ret += f'Weight: {self.weight_lb} lb ({self.weight_kg} kg) [RAW: {self.weight}]\n'
    return ret


def read_nba_team_abbr():
  result = {}
  with open(nba_team_abbr_file_path) as csvfile:
    csv_reader = csv.reader(csvfile, delimiter = '\t')
    for row in csv_reader:
      result[row[1]] = row[0]
  return result


def read_nba_team_div():
  result = {}
  with open(nba_team_div_file_path) as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
      result[row[0]] = [row[1], row[2]]
  return result


def generate_nba_data():
  nba_team_abbr = read_nba_team_abbr()
  nba_team_div = read_nba_team_div()

  players = []
  with open(raw_nba_data_file_path) as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
      player = Player()
      player.last_name, player.first_name = row[3].split(',')
      player.last_name = re.sub(r'\(.*\)', '', player.last_name).strip()
      player.first_name = re.sub(r'\(.*\)', '', player.first_name).strip()
      player.team = nba_team_abbr[row[0]]
      player.team_div = nba_team_div[player.team][0]
      player.team_conf = nba_team_div[player.team][1]
      player.position = row[1]
      player.number = row[2]
      player.height = row[4]
      player.weight = row[5]
      player.dob = row[6]
      player.populate()
      players.append(player)
  return players


def check_team(guess_player: Player, real_player: Player):
  r1 = 'T' if guess_player.team == real_player.team else 'F'
  r2 = 'T' if guess_player.team_conf == real_player.team_conf else 'F'
  r3 = 'T' if guess_player.team_div == real_player.team_div else 'F'
  # r4 = 'T' if guess_player.position == real_player.position else 'F'
  return [r1, r2, r3]


def check_value(guess_player_value: int, real_player_value: int):
  if guess_player_value == real_player_value:
    return 'G'
  diff = 'Y' if abs(guess_player_value - real_player_value) <= 2 else 'B'
  dir = 'U' if guess_player_value - real_player_value < 0 else 'D'
  return f'{diff}{dir}'


def check(guess_player: Player, real_player: Player):
  result = check_team(guess_player, real_player)
  result.append(check_value(guess_player_value=guess_player.height_in, real_player_value=real_player.height_in))
  result.append(check_value(guess_player_value=guess_player.age, real_player_value=real_player.age))
  result.append(check_value(guess_player_value=guess_player.number_int, real_player_value=real_player.number_int))
  return '-'.join(result)


def gen_next(guess_player: Player, candiates: typing.List[Player]):
  result = {}
  longest_branch_len = 0
  for candidate in candiates:
    pattern_key = check(guess_player, candidate)
    if pattern_key not in result:
      result[pattern_key] = []
    result[pattern_key].append(candidate)
    longest_branch_len = max(longest_branch_len, len(result[pattern_key]))
  return result, longest_branch_len


def find_next(guess_players: typing.List[Player], candiates: typing.List[Player]):
  min_max_len = 10000000
  min_max_candidate = None
  min_max_candidate_next = None
  for guess_player in guess_players:
    cur_next, cur_longest_len = gen_next(guess_player, candiates)
    if cur_longest_len < min_max_len:
      min_max_len = cur_longest_len
      min_max_candidate = guess_player
      min_max_candidate_next = cur_next
  return min_max_candidate, min_max_candidate_next


def main():
  guess_players = generate_nba_data()
  candidate_players = generate_nba_data()

  '''
  for p in guess_players:
    if p.last_name == 'Poole':
      poole = p
    if p.last_name == 'Windler':
      windler = p

  print(check(windler, poole))
  '''
  itr = 1
  while len(candidate_players) > 1:
      print(f'Iteration {itr}: =======')

      next_guess, next = find_next(guess_players, candidate_players)
      print(f'Please guess this player')
      print(f'{next_guess}')

      guess_result = input("Enter guess result:")
      guess_result = guess_result.upper()
      candidate_players = next[guess_result]
      print(f'Sure, there are [{len(candidate_players)}] candidates left')
      if len(candidate_players) <= 10:
          print('Candidates are:')
          print([f'{c.first_name} {c.last_name}' for c in candidate_players])
      print('=======\n')
      itr += 1

  if len(candidate_players) == 1:
      print(f'I know the player, it is')
      print(f'{candidate_players[0]}')
  else:
      print(f'No Idea. Sorry')
  print('\n\n')


if __name__ == "__main__":
  main()
