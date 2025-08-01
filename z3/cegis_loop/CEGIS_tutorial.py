from z3 import *

def partial_implementation(f_coeff, f_bias, x_val, s):
    O = Int('O')
    F = Int('F')
    O = f_coeff * x_val
    F = O + f_bias
    return [1]

def impl(coeff, bias, x, s):
    COEFF = Int('COEFF')
    BIAS = Int('BIAS')
    s.add(COEFF == coeff)
    s.add(BIAS == bias)
    return COEFF * x + BIAS

def synthesis_step(cexamples):
    print("Enter synthsis phase")
    # Define f(x) = f_coeff * x + f_bias
    f_coeff = Int('f_coeff')
    f_bias = Int('f_bias')

    # Create a solver to synthesize f(x)
    s = Solver()
    s.reset()

    if not cexamples:
        # If no counterexamples exist yet, try to find any function
        print("No counterexamples yet, synthesizing any possible f(x)...")
        return 0, 0
    else:
        for x_val in cexamples:
            # input bit stream I = [0,0,0,0,...0]
            # Out_spec = spec(I)
            # Out_impl = impl(I, initial_val_of_input_fields)

            # input_field0_path0 = BitVec('input_field0_path0', 8)
            # input_field1_path0 = BitVec('input_field1_path0', 4)
            # input_field2_path0 = BitVec('input_field2_path0', 6)
            # O = implementation(f_coeff, f_bias, x_val, s)
            s.add(f_coeff * x_val + f_bias == x_val + 1)  # g(x) = x + 1

    # Check if the constraints are satisfiable
    if s.check() == sat:
        print("s.check() == sat")
        model = s.model()
        print("model =", model)
        print("model[f_bias] =", model[f_bias])
        print(f_bias in model)
        # Deal with the situation where model does not output everything
        coeff_value = model[f_coeff]
        if coeff_value is not None:
            coeff_value = coeff_value.as_long()
        else:
            coeff_value = 0
        bias_value = model[f_bias]
        if bias_value is not None:
            bias_value = bias_value.as_long()
        else:
            bias_value = 0
        print("coeff_value =", coeff_value, "bias_value =", bias_value)

        return coeff_value, bias_value  # Return synthesized function coefficients
    else:
        # No valid solution found for current counterexamples
        print("No solution found for the given counterexamples.")
        return None

def verification_step(coeff, bias):
    print("Enter verification phase")
    # Try to find a counterexample where f(x) != g(x)
    x = Int('x')
    s = Solver()

    # Constraint: f(x) = coeff * x + bias should equal g(x) = x + 1
    # s.add(coeff * x + bias != x + 1)  # Find a mismatch between f(x) and g(x)
    s.add(impl(coeff, bias, x, s) != x + 1)

    if s.check() == sat:
        model = s.model()
        return model[x].as_long()  # Return the counterexample value for x
    else:
        return None  # No counterexample found, the candidate function is valid

def cegis_loop():
    cexamples = []  # Start with no counterexamples
    maxIter = 10 # Alternatively, we can set it to be # input space.
    for i in range(maxIter):
        print("")
        print("cexamples =", cexamples)
        # Synthesis step: generate a new candidate solution f(x)
        candidate = synthesis_step(cexamples)
        print("where candidate is none or not", candidate == None)
        if candidate is None:
            print("Synthesis failed, no valid function found.")
            return

        coeff, bias = candidate
        print(f"Candidate function: f(x) = {coeff}x + {bias}")

        # Verification step: check if the candidate is valid
        cexample = verification_step(coeff, bias)
        if cexample is None:
            print(f"Valid function found: f(x) = {coeff}x + {bias}")
            return
        else:
            print(f"Counterexample found: x = {cexample}")
            cexamples.append(cexample)  # Add the counterexample for the next round

# Run the CEGIS loop
cegis_loop()