# Factorio Quality Optimizer

This is a tool to optimize the quality of items in Factorio. It tries to find the optimal balance between the number of productivity and quality modules, to maximize the output of best quality items.

## Basic setup

![Basic Setup](factorio_upcycling.PNG)

For each quality tier, you need at least an assembly machine with at least one quality module, except for the highest tier assembly machine, which can be filled with productivity modules. The input for the assembly machines is the output of the previous tier.
Any output that is not the desired quality is recycled, with a recycler filled with quality modules.

The goal is to optimize the number of maximum quality output, given a fixed number of input items.

Note that more machines can be added to the setup, and input does not have to be of the lowest quality.

## Formula

Let's define the following variables:

 - $p_i$ The productivity bonus of the $i$th tier assembly machine (summing over all modules) (5th tier = Legendary, 4th tier = Epic, etc...)
 - $q_i$ The quality bonus of the $i$th tier assembly machine (summing over all modules)
 - $q_r$ The productivity bonus of the recycler
 - $k$ The maximum number of modules for the assembly machines
 - $h_i$ The number of top quality items produced from a set of $Q_i$ quality items needed for the $i$th tier assembly machine to produce one output item.
 - $p$ The best avaliable productivity bonus
 - $q$ The best avaliable quality bonus


Note that $q_r = q * 4$, since the recycler has 4 module slots.

We want to maximize $h_i$. We can express them as follows:

$$
h_5 = p_5
$$

Indeed, there is no need to use quality modules, so assuming base productivity of 1, 

$$
h_5 = k \times p
$$

Then, 

$$
h_4 = h_4 p_4(1 - q_4)\frac{1 - q_r}{4} + h_5 p_4(1 - q_4)\frac{q_r}{4} + p_4q_4
$$

The first term of the sum is if the assembly machine created a Q4 quality item, which was then recycled into Q4 quality input. 
The second term is if the assembly machine created a Q4 quality item, which was then recycled into Q5 quality input. 
The last term is if the assembly machine created a Q5 quality item.

This can be rewritten as:

$$
h_4 = (h_5 \frac{q_r}{1 - q_r} + \frac{4q_4}{(1 - q_4)(1 - q_r)}) / (\frac{4}{(p_4(1 - q_4)(1 - q_r))} - 1) 
$$

This is also the form that is used in the code.

Similarly, we have:

$$
h_3 = h_3 p_3(1 - q_3)\frac{1 - q_r}{4} + h_4 (q_3 + q_r)p_3(1 - q_3)\frac{1 - q_r}{4} + h_5 (q_3 + q_r)p_3(1 - q_3)\frac{q_r}{4} + p_3q_3
$$

The first term of the sum is if the assembly machine created a Q3 quality item, which was then recycled into Q3 quality input. 
The second term is if the assembly machine either 

 - created a Q3 quality item, which was then recycled into Q4 quality input,
 - created a Q4 quality item, which was then recycled into Q4 quality input.

The third term is if the assembly machine either

 - created a Q3 quality item, which was then recycled into Q5 quality input,
 - created a Q4 quality item, which was then recycled into Q5 quality input.

The last term is if the assembly machine created a Q5 quality item.

This can be rewritten as:

$$
h_3 = (h_4(q_3 + q_r) + h_5(q_3 + q_r)\frac{q_r}{1 - q_r} + \frac{4q_3^2}{(1 - q_3)(1 - q_r)}) / (\frac{4}{p_3(1 - q_3)(1 - q_r)} - 1) 
$$

And so on.

## Usage

Call either `main_full` or `main_same`:

```python
	main_full(k, tier, quality)
```

Where:

 - `k` is the maximum number of modules for the assembly machines
 - `tier` is the maximum available tier for the modules
 - `quality` is the maximum available quality for the modules

We assume that when a tier or quality is available, all lower ones are too. In practice, it is always better to use the best modules available.

The function will return the solutions formatted like this one:

```bash
Q3 expected output: 0.16875685353430444901 P:1 Q:3
```

`Q3` means that the result is for the machine with 3rd quality recipe (5 = Legendary, 4 = Epic, etc...). The number after P is the number of productivity modules, and the number after Q is the number of quality modules for this machine.

The function also produces csv files, which contains results for all possible combinations of modules.

 `main_full` tries all possible combinations of modules, while `main_same` only tries combinations where productivity and quality modules have the same tier and quality.

 In practice, both seem to return the same results, but `main_same` is faster, and produce smaller csv files.

 If Epic and Legendary qualities are not available, use Q5 for the highest quality tier (Rare), and Q3 for common. If Epic is available, but not legendary, use Q5 for Epic and Q2 for common.

