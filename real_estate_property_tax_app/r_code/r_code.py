r_code = """
perform_analysis <- function(atr_calc, values) {
  # Combine the two datasets into a single dataset
  merged_data <- atr_calc
  merged_data$v1 <- as.numeric(as.character(merged_data$v1))
  merged_data$v2 <- as.numeric(as.character(merged_data$v2))
  merged_data$v3 <- as.numeric(as.character(merged_data$v3))
  merged_data$prop_val <- as.numeric(as.character(merged_data$prop_val))
  merged_data$group_type <- as.numeric(as.character(merged_data$group_type))
  merged_data$atr <- as.numeric(as.character(merged_data$atr))
  
  
  
  
  # Calculate the average atr for each value_bin when group_type is 1
  average_atr <- with(merged_data, tapply(atr[group_type == 1], value_bin[group_type == 1], mean))
  
  # Replace atr values where atr is 0 and group_type is 1 with the average atr for the same value_bin
  merged_data$atr[merged_data$atr == 0 & merged_data$group_type == 1] <- with(merged_data, average_atr[value_bin[atr == 0 & group_type == 1]])
  
  # Check if all values within a value_bin are 0 and drop those observations
  to_drop <- with(merged_data, tapply(atr, value_bin, function(x) all(x == 0)))
  merged_data <- merged_data[!(merged_data$value_bin %in% names(to_drop) & to_drop[as.character(merged_data$value_bin)]), ]
  
  # Check if the total number of observations for group_type == 1 is less than 12
  #  if (sum(merged_data$group_type == 1) < 12) {
  #    message("We can't proceed further. Thanks.")
  #  } else {
  #    # Ensure that the result is numeric
  #    merged_data$atr <- as.numeric(as.character(merged_data$atr))
  #    # Continue with further processing if needed
  #  }
  
  
# 4. Run the restricted spline
  
## 4.1 grab the knots of the spline implied in the vs in the survey responses
  
  df <- merged_data

  df$lprop_val <- log(df$prop_val)
  ## knots:
  k1 <- df %>%
    subset(v2 != 0 & v3 == 0) %>%
    mutate(k1val = lprop_val - v2)
  k1 <- mean(k1$k1val)
  k2 <- df %>%
    subset(v3 != 0) %>%
    mutate(k2val = lprop_val - v3)
  k2 <- mean(k2$k2val)
  
  
## 4.2 set up the restrictions on the spline
  vmin <- 12
  vmax <- 21
  
  
## specify the restriction matrix. Restriktor wants it in the form R * \theta >= rhs
  myConstraints <- rbind(c(1, vmin, 0, 0),                     # 1. above 0 at vmin
                         c(-1, -vmin, 0, 0),                   # 2. below 100 at vmin
                         c(1, k1, 0, 0),                       # 3. above 0 at k1
                         c(-1, -k1, 0, 0),                     # 4. below 100 at k1
                         c(1, k1, (k2 - k1), 0),               # 5. above 0 at k2
                         c(-1, -k1, -(k2 - k1), 0),            # 6. below 100 at k2
                         c(1, k1, (k2 - k1), (vmax - k2)),     # 7. above 0 at vmax
                         c(-1, -k1, -(k2 - k1), -(vmax - k2))) # 8. below 100 at vmax
  
  myRhs <- c(0, -100, 0, -100, 0, -100, 0, -100)

##################### 
df <- df %>%mutate(atr=atr/100)
#####################  
## 4.3 run the unrestricted spline
  cspline <-
    lm(
      atr ~ v1 + v2 + v3,
      data = df
    )
  
## 4.4 run the restricted spline and summarize the outputs.
  restr.cspline <-
    restriktor(
      cspline, 
      constraints = myConstraints,
      rhs = myRhs,
      mix.weights = "boot",
      se = "none"
    )
  summary(restr.cspline)
  rm(cspline)


  
# 5. Use the spline coefficients to compute revenue from respondent's response property type
  
## respondents are either "Rented" or "Self-occupied"
  
## refer to the equation in the overleaf being computed.
  
## 5.1 Grab the coefficients
  coefficients <-
    coef(
      summary(
        restr.cspline
      )
    )
  rm(restr.cspline)
  beta0 <- coefficients[1]  # Intercept
  beta1 <- coefficients[2] 
  beta2 <- coefficients[3]
  beta3 <- coefficients[4]
  rm(coefficients)
  
  
## 5.2 Grab the Vxs as described in equations (7) -- (10)
  
  V <- 
    ifelse(
      df$onlyocc[[1]] == "Rented",
      values$v_1[[1]],
      ifelse(
        df$onlyocc[[1]] == "Self-occupied",
        values$v_1[[2]],
        NA
      )
    ) # equation (7)
  V1 <-
    ifelse(
      df$onlyocc[[1]] == "Rented",
      values$v_v1_1[[1]],
      ifelse(
        df$onlyocc[[1]] == "Self-occupied",
        values$v_v1_1[[2]],
        NA
      )
    ) # equation (8)
  V2 <- 
    ifelse(
      df$onlyocc[[1]] == "Rented",
      values$v_v2_1[[1]],
      ifelse(
        df$onlyocc[[1]] == "Self-occupied",
        values$v_v2_1[[2]],
        NA
      )
    ) # equation (9)
  V3 <-
    ifelse(
      df$onlyocc[[1]] == "Rented",
      values$v_v3_1[[1]],
      ifelse(
        df$onlyocc[[1]] == "Self-occupied",
        values$v_v3_1[[2]],
        NA
      )
    ) # equation (10)
  
  
## 5.3 compute equation (6), the total tax demand from the respondent's property type. Dividing by 100 since the ATR elicited from the respondent runs from 0 to 100 not from 0 to 1.
  R1 <- (beta0 * V + beta1 * V1 + beta2 * V2 + beta3 * V3) / 100
  
  
# 6. Scale up to get total tax demand and back down again to get the projected revenue using equation (15)
  
  D1 <- ifelse(
    df$onlyocc[[1]] == "Rented",
    427526034,
    ifelse(
      df$onlyocc[[1]] == "Self-occupied",
      916227952,
      NA
    )
  ) # equation (11), total tax demand from the respondent's property type
  
  T <- 5450337792 # equation (14), total tax revenue actually paid
  
  R <-
    ((T / D1) * R1)/1e9 # equation (15) our projected revenue from the respondent's preferred tax schedule. Measured in billions of Rupees since we show it to the respondent.
  
  revenue <- data.frame(revenue=R) 
  total_revenue <- revenue %>%
    summarise(total_revenue = sum(revenue)) %>%
    mutate(current_revenue = 5.45) %>%
    mutate(gap = total_revenue - current_revenue) 
  
  return(total_revenue)
  print("code_chunk_4")
}
"""