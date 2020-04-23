DROP DATABASE in_it_to_winnik;
CREATE DATABASE in_it_to_winnik;
USE in_it_to_winnik;

CREATE TABLE league (
  id int PRIMARY KEY AUTO_INCREMENT,
  yahoo_id int,
  yahoo_key varchar(40),
  name varchar(40),
  url varchar(255),
  num_teams int,
  weekly_deadline boolean,
  scoring_type varchar(255),
  start_date date,
  end_date date,
  start_week int,
  end_week int
);

CREATE TABLE scoring_category (
  id int PRIMARY KEY AUTO_INCREMENT,
  category_name varchar(40),
  category_abbreviation varchar(5),
  position_type varchar(40)
);

-- junction table between league and scoring category
CREATE TABLE league_scoring_category (
  league_id int,
  category_id int,
  PRIMARY KEY (league_id, category_id),
  -- both tables need to be already created
  FOREIGN KEY (league_id) REFERENCES league (id),
  FOREIGN KEY (category_id) REFERENCES scoring_category (id)
);

CREATE TABLE week (
-- using id here because matchup references fantasy_team
  id int PRIMARY KEY AUTO_INCREMENT,
  league_id int,
  week_number int,
  start_date date,
  end_date date
);

CREATE TABLE fantasy_team (
  id int PRIMARY KEY AUTO_INCREMENT,
  yahoo_key varchar(40),
  yahoo_id int,
  name varchar(40),
  logo_url varchar(255),
  manager varchar(200),
  league_id int
);

CREATE TABLE matchup (
  id int PRIMARY KEY AUTO_INCREMENT,
--  home and away are arbitrary discriminators, and not reflected in the yahoo league in any way
  home_id int,
  away_id int,
--  home_score int,
--  away_score int,
-- using week_id instead of week because different leagues have different week structures
  week_id int
);

CREATE TABLE roster (
  id int PRIMARY KEY AUTO_INCREMENT,
  team_id int,
  player_id int,
--  includes 'BN' and 'Util'
  selected_position varchar(10),
  start_date date,
  end_date date
);

CREATE TABLE player (
  id int PRIMARY KEY AUTO_INCREMENT,
--  using NHL's first and last name, not Yahoo's
  first_name varchar(40),
  last_name varchar(40),
  yahoo_id int,
  yahoo_key varchar(40),
  nhl_id int,
  birth_date date,
  birth_state_province varchar(5),
  nationality varchar(40),
  height int,
  weight int
);

CREATE TABLE skater_stats (
  id int PRIMARY KEY AUTO_INCREMENT,
  skater_id int,
  time_on_ice varchar(10),
  assists int,
  goals int,
  shots int,
  hits int,
  powerplay_goals int,
  powerplay_assists int,
  penalty_minutes int,
  faceoff_wins int,
  faceoff_percentage decimal(6,5),
  takeaways int,
  giveaways int,
  shorthanded_goals int,
  shorthanded_assists int,
  blocked_shots int,
  plus_minus int,
  even_strength_toi varchar(10),
  powerplay_toi varchar(10),
  shorthanded_toi varchar(10),
  date_ date
);

CREATE TABLE goalie_stats (
  id int PRIMARY KEY AUTO_INCREMENT,
  goalie_id int,
  time_on_ice varchar(10),
  shots_against int,
  saves int,
  goals_against int,
  save_percentage decimal(6,5),
  shorthanded_shots_against int,
  shorthanded_saves int,
  shorthanded_save_percentage decimal(6,5),
  date_ date
);

-- these last 2 tables are irrelevant at the moment due to design change
CREATE TABLE player_nhl_team (
  id int PRIMARY KEY AUTO_INCREMENT,
  player_id int,
  start_date date,
  end_date date,
--  nhl team's nhl.com id
  nhl_id int
);

-- don't really need to add a new ID here
CREATE TABLE nhl_team (
  nhl_id int PRIMARY KEY,
  name varchar(40),
  abbreviation varchar(5)
);

-- it's better to use these to avoid having to worry about if the table is created yet
ALTER TABLE week ADD FOREIGN KEY (league_id) REFERENCES league (id);

ALTER TABLE fantasy_team ADD FOREIGN KEY (league_id) REFERENCES league (id);

ALTER TABLE matchup ADD FOREIGN KEY (home_id) REFERENCES fantasy_team (id);

ALTER TABLE matchup ADD FOREIGN KEY (away_id) REFERENCES fantasy_team (id);

ALTER TABLE matchup ADD FOREIGN KEY (week_id) REFERENCES week (id);

ALTER TABLE roster ADD FOREIGN KEY (team_id) REFERENCES fantasy_team (id);

ALTER TABLE roster ADD FOREIGN KEY (player_id) REFERENCES player (id);

ALTER TABLE skater_stats ADD FOREIGN KEY (skater_id) REFERENCES player (id);

ALTER TABLE goalie_stats ADD FOREIGN KEY (goalie_id) REFERENCES player (id);

ALTER TABLE player_nhl_team ADD FOREIGN KEY (player_id) REFERENCES player (id);

ALTER TABLE player_nhl_team ADD FOREIGN KEY (nhl_id) REFERENCES nhl_team (nhl_id);
