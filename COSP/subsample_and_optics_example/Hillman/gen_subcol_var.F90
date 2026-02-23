! ****************************************************************************
! Generate condensate with subgrid variability using algorithm described in
! Raisanen et al. (2004).
!
! Inputs:
!     cb(npts, nlev)        binary clear/cloudy flag
!     qmean(npts, nlev)     gridbox-mean condensate amount by level
!     rho(npts, nlev)       rank correlation of cloudy parts of adjacent layers
!     seed                  initial seed value for random number generator
!
! Outputs:
!     q(npts, ncol, nlev)      cloudy/clear flag (1 -> cloud, 0 -> clear)
!
! NOTE:   Inputs MUST be from TOA to surface!
! AUTHOR: Benjamin R. Hillman
! DATE:   12 March 2016
! ****************************************************************************
subroutine gen_subcol_var(npts, ncol, nlev, cb, &
                          qmean, q, T,tca, seed)
    !f2py integer, intent(in) :: npts, ncol, nlev
    !f2py real, intent(in) :: cb(npts, ncol, nlev)
    !f2py real, intent(in) :: qmean(npts, nlev) 
    !f2py integer, intent(in) :: seed=0
    !f2py real, intent(out) :: q(npts, ncol, nlev)

    use random
    use sort
    implicit none

    ! inputs
    integer, intent(in) :: npts, ncol, nlev
    real, intent(in) :: cb(npts, ncol, nlev) ! cloudy flag
    real, intent(in) :: qmean(npts, nlev),T(npts, nlev),tca(npts, nlev) ! condensate mean, temperature and cloud frac
    integer, intent(in) :: seed ! seed for random number generator

    ! outputs
    real, intent(out) :: q(npts, ncol, nlev) ! subcolumn condensate
      
    ! local variables
    real, dimension(npts, ncol, nlev) :: y  ! y(i, j, k) from R04
    real, dimension(npts, ncol, nlev) :: rn1, rn2, rn3  ! random numbers
    real :: kappa, theta  ! distribution parameters
    integer :: i, j, k, l  ! loop indices
    integer, parameter :: nsamples = 10000
    real, dimension(nsamples) :: x, cdf  ! sample of variates to build CDF
    integer, dimension(nsamples) :: xi  ! sort indices from cdf

    real, dimension(npts, nlev) :: rho ! rank correlation
    real :: sum_var
    rho(:,:)=1.
    ! initialize psuedo-random number generator
    if (seed /= 0) then
        print *, 'Initializing random seed from gen_subcol_var'
        call init_random_seed(seed)
    end if

    ! generate random numbers
    call random_number(rn1)
    call random_number(rn2)
    call random_number(rn3)

    ! calculate y(i,j)
    ! NOTE: inputs must be from TOA to surface!!!
    y(:, :, 1) = rn1(:, :, 1)
    do k = 2, nlev
        where (rn2(:, :, k) <= spread(rho(:, k), 2, ncol))
            y(:, :, k) = y(:, :, k - 1) 
        elsewhere
            y(:, :, k) = rn3(:, :, k)
        endwhere
    end do

    ! generate distributions of condensate
    ! The variable cdf is a "fake" CDF; we will generate a sample of
    ! gamma-distributed variates and sort them. cdf then will give the
    ! fraction of the sample with values below each sorted value.
    do l = 1, nsamples
        cdf(l) = 1.0 * l / nsamples
    end do

    ! initialize condensate
    q = 0.0

    do i = 1, npts
        do k = 1, nlev
            if (T(i,nlev+1-k).lt.235.15) then !condition for cirrus scheme activation of LMDZ: added by pg
            !if (T(i,k).lt.235.15) then !condition for cirrus scheme activation of LMDZ: added by pg
                    ! make sure we have some condensate
            if (all(cb(i, :, k) == 0) .or. qmean(i, k) <= 0) then
                cycle
            !else if (qmean(i, k) < 1e-15 .or. qvar(i, k) < 1e-15) then
            else if (qmean(i, k) <= 0) then
                !print *, 'WARNING: cloud present, but all condensate zero'
                cycle
            else if (isnan(qmean(i, k))) then
                !print *, 'WARNING: cloud present, but all condensate nan'
                cycle
            end if

            ! calculate distribution parameters from mean and variance
            ! NOTE: obtained via method of moments
            !____________values for qi gamma distribution of cirrus clouds in Borella 2024.
            kappa = 4/3
            theta = qmean(i, k)/tca(i,k)
            if (kappa <= 0 .or. theta <= 0) then
                print *, 'WARNING: distribution params not calculated'
                cycle
            end if

            ! Generate a sample of gamma-distributed random variates.
            ! Functions in random.f90 use a flag to indicate whether or
            ! not distribution parameters have changed. Either set the first
            ! call with .true., or set each call with .false.?
            x(1) = random_gamma(kappa, .true.)
            do l = 1, nsamples
                ! make sure we don't get zeros
                x(l) = 0
                do while (x(l) == 0)
                    x(l) = random_gamma(kappa, .false.) * theta
                end do
            end do

            ! sort condensate values so cdf above actually corresponds to
            ! the empirical CDF of this sample

            call quick_sort(x, xi)

            !print *, 'before pb: xi', xi
            ! loop over subcolumns and find value of condensate from sample x 
            ! such that the cdf of the sample x is closest to y(i, j, k)
            do j = 1, ncol
                if (cb(i, j, k) > 0) then
                    q(i, j, k) = x(minloc(abs(cdf - y(i, j, k)), 1))
                else
                    q(i, j, k) = 0.0
                end if
            end do

            else 

            do j = 1, ncol
              if (cb(i, j, k) > 0) then
                q(i, j, k) = qmean(i, k)/tca(i,k)
              endif
            end do
            endif ! temperature condition added by pg
       end do
    end do
end subroutine
