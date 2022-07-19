# https://stats.stackexchange.com/questions/64482/null-hypothesis-of-the-wald-wolfowitz-runs-test
ww_test <- function(x) {
  x <- factor(x)
  n <- length(x)
  njs <- table(x)
  njs <- structure(.Data=as.vector(njs), .Names=names(njs))
  mu <- (n*(n+1) - sum(njs^2))/n
  sdev_l <- n^2*(n-1)
  sdev_u <- sum(njs^2*(sum(njs^2)+n*(n+1))) - 2*n*sum(njs^3)-n^3
  sdev <- sqrt(sdev_u/sdev_l)
  r <- sum(diff(as.numeric(x)) != 0) + 1
  z <- (r - mu) / sdev
  pvalue <- 2*pnorm(-abs(z))
  return(pvalue)
}

L = c(0, 0, 1, 1, 2, 2, 2, 2, 1, 0, 0, 1)
ww_test(L)
