library(readr)
library(dplyr)
library(ggplot2)
library(tidyr)

#read in player data
player_data <- read_csv("player-combined-data.csv")

#filter to 2024 data
player_data_2024 <- player_data %>% filter(year == 2024)

#seperate into confrence vs non confrence play
player_data_2024_NC <- player_data_2024 %>% filter(Competition == "United States. NCAA D1 Non-conference matches")
player_data_2024_C <- player_data_2024 %>% filter(Competition == "United States. NCAA D1 Big Ten")

#select only defenders (players that played on the "backline")
player_data_2024_backline_NC <- player_data_2024_NC %>% filter(grepl("b", Position, ignore.case = TRUE))
player_data_2024_backline_C <- player_data_2024_C %>% filter(grepl("b", Position, ignore.case = TRUE))

#calculate the average per game stats of defensive metrics in non conference play
player_data_2024_backline_NC_stats <- player_data_2024_backline_NC %>%
  select(
    player_name,
    team,
    Match,
    year,
    Position,
    defensive_duels,
    defensive_duels_won,
    loose_ball_duels,
    loose_ball_duels_won,
    interceptions,
    losses,
    losses_in_own_half,
    clearances
  ) %>%
  group_by(team, Match) %>%  
  mutate(
    total_defensive_duels = sum(defensive_duels, na.rm = TRUE),
    total_defensive_duels_won = sum(defensive_duels_won, na.rm = TRUE),
    total_loose_ball_duels = sum(loose_ball_duels, na.rm = TRUE),
    total_loose_ball_duels_won = sum(loose_ball_duels_won, na.rm = TRUE),
    total_interceptions = sum(interceptions, na.rm = TRUE),
    total_losses = sum(losses, na.rm = TRUE),
    total_losses_in_own_half = sum(losses_in_own_half, na.rm = TRUE),
    total_clearances = sum(clearances, na.rm = TRUE)
  ) %>%
  ungroup() %>%
  group_by(team) %>%  
  summarize(
    avg_defensive_duels = mean(total_defensive_duels, na.rm = TRUE),
    avg_defensive_duels_won = mean(total_defensive_duels_won, na.rm = TRUE),
    avg_loose_ball_duels = mean(total_loose_ball_duels, na.rm = TRUE),
    avg_loose_ball_duels_won = mean(total_loose_ball_duels_won, na.rm = TRUE),
    avg_interceptions = mean(total_interceptions, na.rm = TRUE),
    avg_losses = mean(total_losses, na.rm = TRUE),
    avg_losses_in_own_half = mean(total_losses_in_own_half, na.rm = TRUE),
    avg_clearances = mean(total_clearances, na.rm = TRUE)
  ) %>%
  mutate(
    avg_Defensive_duel_win_pct = ifelse(avg_defensive_duels == 0, NA, avg_defensive_duels_won / avg_defensive_duels),
    avg_Loose_ball_duel_win_pct = ifelse(avg_loose_ball_duels == 0, NA, avg_loose_ball_duels_won / avg_loose_ball_duels),
    source = "Non-Conference"
  )

#calculate the average per game stats of defensive metrics in conference play
player_data_2024_backline_C_stats <- player_data_2024_backline_C %>%
  select(
    player_name,
    team,
    Match,
    year,
    Position,
    defensive_duels,
    defensive_duels_won,
    loose_ball_duels,
    loose_ball_duels_won,
    interceptions,
    losses,
    losses_in_own_half,
    clearances
  ) %>%
  group_by(team, Match) %>%  
  mutate(
    total_defensive_duels = sum(defensive_duels, na.rm = TRUE),
    total_defensive_duels_won = sum(defensive_duels_won, na.rm = TRUE),
    total_loose_ball_duels = sum(loose_ball_duels, na.rm = TRUE),
    total_loose_ball_duels_won = sum(loose_ball_duels_won, na.rm = TRUE),
    total_interceptions = sum(interceptions, na.rm = TRUE),
    total_losses = sum(losses, na.rm = TRUE),
    total_losses_in_own_half = sum(losses_in_own_half, na.rm = TRUE),
    total_clearances = sum(clearances, na.rm = TRUE)
  ) %>%
  ungroup() %>%
  group_by(team) %>%  
  summarize(
    avg_defensive_duels = mean(total_defensive_duels, na.rm = TRUE),
    avg_defensive_duels_won = mean(total_defensive_duels_won, na.rm = TRUE),
    avg_loose_ball_duels = mean(total_loose_ball_duels, na.rm = TRUE),
    avg_loose_ball_duels_won = mean(total_loose_ball_duels_won, na.rm = TRUE),
    avg_interceptions = mean(total_interceptions, na.rm = TRUE),
    avg_losses = mean(total_losses, na.rm = TRUE),
    avg_losses_in_own_half = mean(total_losses_in_own_half, na.rm = TRUE),
    avg_clearances = mean(total_clearances, na.rm = TRUE)
  ) %>%
  mutate(
    avg_Defensive_duel_win_pct = ifelse(avg_defensive_duels == 0, NA, avg_defensive_duels_won / avg_defensive_duels),
    avg_Loose_ball_duel_win_pct = ifelse(avg_loose_ball_duels == 0, NA, avg_loose_ball_duels_won / avg_loose_ball_duels),
    source = "Conference"
  )

#combine the data for plotting
player_data_2024_backline_combined <- bind_rows(player_data_2024_backline_C_stats,player_data_2024_backline_NC_stats)

#write.csv(player_data_2024_backline_C_stats, "Team Defense Stats Confrence Play.csv", row.names = F)
#write.csv(player_data_2024_backline_NC_stats, "Team Defense Stats Non Confrence Play.csv", row.names = F)

# Filter the data for Northwestern
NW_data <- player_data_2024_backline_combined %>%
  filter(team == "Northwestern Wildcats")

# Reshaping the data to long format for easier plotting
NW_data_long <- NW_data %>%
  pivot_longer(
    cols = starts_with("avg_"), 
    names_to = "stat", 
    values_to = "value"
  )

#Compare duel winning pct
NW_data_long_pct <- NW_data_long %>% filter(stat %in% c("avg_Loose_ball_duel_win_pct", "avg_Defensive_duel_win_pct"))

ggplot(NW_data_long_pct, aes(x = stat, y = value, fill = source)) +
  geom_bar(stat = "identity", position = "dodge") +  
  labs(
    title = "Comparison of Northwestern's Stats by Conference Play vs Non-Conference Play",
    x = "Statistic",  
    y = "Stat Value"  
  ) +
  scale_fill_manual(values = c("Conference" = "blue", "Non-Conference" = "red")) +  
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),  
    axis.title.x = element_text(size = 12), 
    axis.title.y = element_text(size = 12)   
  )

#compare defensive stats 
NW_data_long_totals <- NW_data_long %>% filter(!stat %in% c("avg_Loose_ball_duel_win_pct", "avg_Defensive_duel_win_pct"))

ggplot(NW_data_long_totals, aes(x = stat, y = value, fill = source)) +
  geom_bar(stat = "identity", position = "dodge") +  
  labs(
    title = "Comparison of Northwestern's Stats by Conference Play vs Non-Conference Play",
    x = "Statistic",  
    y = "Stat Value"  
  ) +
  scale_fill_manual(values = c("Conference" = "blue", "Non-Conference" = "red")) +  
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),  
    axis.title.x = element_text(size = 12), 
    axis.title.y = element_text(size = 12)   
  )

#calculate the averages for tournament bound teams
tournament_player_data_2024_backline_C_stats <- player_data_2024_backline_C_stats %>%
  filter(team %in% c("UCLA Bruins", "Michigan Wolverines", "Ohio State Buckeyes", "Indiana Hoosiers", "Washington Huskies","	
Maryland College Park Terrapins"))

tournament_teams_average_stats <- tournament_player_data_2024_backline_C_stats %>%
  summarize(
    avg_defensive_duels = mean(avg_defensive_duels, na.rm = TRUE),
    avg_defensive_duels_won = mean(avg_defensive_duels_won, na.rm = TRUE),
    avg_loose_ball_duels = mean(avg_loose_ball_duels, na.rm = TRUE),
    avg_loose_ball_duels_won = mean(avg_loose_ball_duels_won, na.rm = TRUE),
    avg_interceptions = mean(avg_interceptions, na.rm = TRUE),
    avg_losses = mean(avg_losses, na.rm = TRUE),
    avg_losses_in_own_half = mean(avg_losses_in_own_half, na.rm = TRUE),
    avg_clearances = mean(avg_clearances, na.rm = TRUE),
    avg_Defensive_duel_win_pct = mean(avg_Defensive_duel_win_pct, na.rm = TRUE),
    avg_Loose_ball_duel_win_pct = mean(avg_Loose_ball_duel_win_pct, na.rm = TRUE)
  ) %>%
  mutate(source = "Conference", 
         team = "Tournament Teams") %>%
  select(team, everything())

NW_tournament_comp <- rbind(tournament_teams_average_stats,NW_data) %>% filter(source == "Conference")

# Reshaping the data to long format for easier plotting
tournament_data_long <- NW_tournament_comp %>%
  pivot_longer(
    cols = starts_with("avg_"), 
    names_to = "stat", 
    values_to = "value"
  )

#Compare duel winning pct
tournament_data_long_pct <- tournament_data_long %>% filter(stat %in% c("avg_Loose_ball_duel_win_pct", "avg_Defensive_duel_win_pct"))

ggplot(tournament_data_long_pct, aes(x = stat, y = value, fill = team)) +
  geom_bar(stat = "identity", position = "dodge") +  
  labs(
    title = "Comparison of Northwestern's Duel Stats vs Tournament Bound Teams",
    x = "Statistic",  
    y = "Stat Value"  
  ) +
  scale_fill_manual(values = c("Tournament Teams" = "red", "Northwestern Wildcats" = "purple")) +  
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),  
    axis.title.x = element_text(size = 12), 
    axis.title.y = element_text(size = 12)   
  )

#compare defensive stats 
tournament_data_long_totals <- tournament_data_long %>% filter(!stat %in% c("avg_Loose_ball_duel_win_pct", "avg_Defensive_duel_win_pct"))

ggplot(tournament_data_long_totals, aes(x = stat, y = value, fill = team)) +
  geom_bar(stat = "identity", position = "dodge") +  
  labs(
    title = "Comparison of Northwestern's Defense Stats vs Tournament Bound Teams",
    x = "Statistic",  
    y = "Stat Value"  
  ) +
  scale_fill_manual(values = c("Tournament Teams" = "red", "Northwestern Wildcats" = "purple")) +  
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),  
    axis.title.x = element_text(size = 12), 
    axis.title.y = element_text(size = 12)   
  )

