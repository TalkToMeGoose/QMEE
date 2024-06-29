# Load required libraries
library(tidyverse)
library(readr)

# Function to load and process data
load_and_process_data <- function() {
  # Construct the file path
  file_path <- "data/ACTUAL_EXP_CREAMERY_QMEESS24.csv"
  
  
  # Check if the file exists
  if (!file.exists(file_path)) {
    stop("Data file not found. Please ensure 'ACTUAL_EXP_CREAMERY_QMEESS24.csv' is in the 'data' folder.")
  }
  
  # Read the CSV file
  df <- read_csv(file_path)
  
  # Extract survey responses
  survey_responses <- df %>%
    select(
      participant_id = `participant.id_in_session`,
      participant_label = `participant.label`,
      altruism = `centipede_game.4.player.altruism`,
      trust = `centipede_game.4.player.trust`,
      risk_tolerance = `centipede_game.4.player.risk_tolerance`,
      greed = `centipede_game.4.player.greed`,
      desire_to_win = `centipede_game.4.player.desire_to_win`
    ) %>%
    mutate(across(altruism:desire_to_win, ~as.numeric(as.character(.))))  # Convert to numeric
  
  # Restructure the game data
  restructured_data <- df %>%
    pivot_longer(
      cols = starts_with("centipede_game."),
      names_to = c("round", ".value"),
      names_pattern = "centipede_game\\.(\\d+)\\.(.+)",
      values_drop_na = TRUE
    ) %>%
    select(
      participant_id = `participant.id_in_session`,
      participant_label = `participant.label`,
      round,
      group_id = `group.id_in_subsession`,
      role = `player.id_in_group`, # indicates first-mover (1) or second mover (2)
      treatment = `group.treatment`,
      node_reached = `group.node`,
      payoff = `player.payoff`,
      treatment_order = `group.treatment_order`,
      large_pile_end = `group.large_pile_end`,
      small_pile_end = `group.small_pile_end`
    ) %>%
    mutate(
      round = as.integer(round),
      group_id = as.integer(group_id),
      role = as.integer(role),
      node_reached = as.integer(node_reached),
      payoff = as.numeric(payoff),
      large_pile_end = as.numeric(large_pile_end),
      small_pile_end = as.numeric(small_pile_end)
    )
  
  # Join game data with survey responses
  final_data <- restructured_data %>%
    left_join(survey_responses, by = c("participant_id", "participant_label"))
  
  # Sort the data by group_id, then round, then role
  sorted_data <- final_data %>%
    arrange(group_id, round, role)
  
  return(sorted_data)
}

# Function to save processed data
save_processed_data <- function(data, filename = "processed_centipede_game_data.csv") {
  write_csv(data, file.path("data", filename))
}

# Main processing function
main <- function() {
  data <- load_and_process_data()
  save_processed_data(data)
  return(data)
}

# Run the main function if this script is run directly
if (sys.nframe() == 0) {
  data <- main()
  print(head(data))  # Print the first few rows to check the output
}
