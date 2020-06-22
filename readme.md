## The 538 Riddler - June 19 2020

The way I am going to do this is to use integer programming to find solutions to this. Specifically, I use OR-Tools to set up a system of constraints that then gets solved. 

Writing the volume of the sphere in terms of diameter out, we note that there is a bunch of constants out front which don't matter for the actual proportioning

![formulation](images/sphere_volume.png)

What we actually care about is finding the way to group the first *S* integers into *N* group such that the sum of each group is equal. Each group can then be multiplied by the constants in front of the volume formula to get the final volume. 

We can formulate this mathematically as

![formulation](images/formulation.png)

Where *n* is group number, and 𝛿<sub>s,n</sub> is an indicator variable  (e.g. it is zero or one) denoting that *s* is in group *n*. The first equation says that each group must sum the same thing, 1/N of the total volume (ignoring constants).

The second says that each sphere must be represented in exactly one group (recall that the indicator variable is either zero or one)

The grouping problem then becomes finding 𝛿<sub>s,i</sub> for a given *N* and *S*. A solution to this may or may not exist (for example there is no way to do *N*=3, *S*=3)

The problem as stated becomes finding the minimum S for which a solution exists.

## Code
I wrote an solver of the constraints above using OR-Tools. This code has two modes. One mode will both scan over *all* possible combinations of *N* and *S* less than certain bounds to make a plot of which *N*, *S* pairs are possible. The other mode will find the minimun *N*, *S* pair that is possible.

There are a few ways to speed this code up dramatically that I built in

- If the sum of the spheres is not divisible by *N* we immediately know it's not possible to split this evenly
- Always assign the largest sphere to the first group. This breaks the symmetry around group numbering
- If the nth and n-1th sphere volume is larger than the volume of all the spheres divided by the number of piles, they have to be in a separate group. This lets us place some spheres in separate groups and speeds things up considerably.

## Results
Running this, I find

| Number of Piles | Minimum Number of Spheres |
|-----------------|---------------------------|
| 1               | 1                         |
| 2               | 12                        |
| 3               | 23                        |
| 4               | 24                        |
| 5               | 24                        |
| 6               | 35                        |
| 7               | 41                        |
| 8               | 47                        |
| 9               | 53                        |
| 10              | 59                        |
| 11              | 54, 65, 66 or >70         |

We can plot this, and see that it kinda looks linear-ish which gives us a guess that 11 piles will need around 65 spheres, and 12 piles will need around 71 spheres.
![formulation](images/plot.png)