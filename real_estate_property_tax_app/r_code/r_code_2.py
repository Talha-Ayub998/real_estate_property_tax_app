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
  
  svy_dta <- merged_data

  svy_dta$lprop_val <-
    log(svy_dta$prop_val)
  k1 <- svy_dta %>%
    subset(
      v2 != 0 & 
        v3 == 0
    ) %>%
    mutate(
      k1val = lprop_val - v2
    )
  k1 <-
    mean(k1$k1val)
  k2 <- svy_dta %>%
    subset(
      v3 != 0
    ) %>%
    mutate(
      k2val = lprop_val - v3
    )
  k2 <- 
    mean(k2$k2val)
  
  ## 3.2 set up the restrictions on the spline
  vmin <- 12
  vmax <- 21
  ### specify the restriction matrix. Restriktor wants it in the form R * \theta >= rhs
  myConstraints <- 
    rbind(
      c(1, vmin, 0, 0),                     # 1. above 0 at vmin
      c(-1, -vmin, 0, 0),                   # 2. below 100 at vmin
      c(1, k1, 0, 0),                       # 3. above 0 at k1
      c(-1, -k1, 0, 0),                     # 4. below 100 at k1
      c(1, k1, (k2 - k1), 0),               # 5. above 0 at k2
      c(-1, -k1, -(k2 - k1), 0),            # 6. below 100 at k2
      c(1, k1, (k2 - k1), (vmax - k2)),     # 7. above 0 at vmax
      c(-1, -k1, -(k2 - k1), -(vmax - k2))  # 8. below 100 at vmax
    )
  myRhs <-
    c(0, -100, 0, -100, 0, -100, 0, -100)
  
  ## 3.3 run the unrestricted spline
  cspline <-
    lm(
      atr ~ v1 + v2 + v3,
      data = svy_dta
    )
  
  ## 3.4 run the restricted spline
  restr.cspline <-
    restriktor(
      cspline,
      constraints = myConstraints,
      rhs = myRhs,
      se = "none"
    )
  
  #' 4. Display spline.
  eq = function(x){
    restr.cspline$b.restr[1] + 
      (restr.cspline$b.restr[2] * x) + 
      ((restr.cspline$b.restr[3] - restr.cspline$b.restr[2]) * (x - k1) * (x > k1)) + 
      ((restr.cspline$b.restr[4] - restr.cspline$b.restr[3]) * (x - k2) * (x > k2))
  }
  
  
  spline_df <- data.frame(lprop_val = seq(vmin, vmax, length.out = 100)) %>%
    mutate(spline_val = Vectorize(eq)(lprop_val))
  
  return(spline_df)
  print("code_chunk_4")
  
}
"""