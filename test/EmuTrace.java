// Debug helper: step the emulator from a word address and print the execution address and a few registers.
// Script args: <start-word-hex> <steps> [reg ...]     (SP is preset to 0x200)
//@category Testing
import ghidra.app.emulator.EmulatorHelper;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;

public class EmuTrace extends GhidraScript {
	@Override
	protected void run() throws Exception {
		String[] a = getScriptArgs();
		Address start = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(Long.parseLong(a[0], 16) * 2);
		disassemble(start);
		EmulatorHelper emu = new EmulatorHelper(currentProgram);
		emu.writeRegister("SP", 0x200);
		emu.writeRegister(emu.getPCRegister(), start.getAddressableWordOffset());
		for (int i = 0; i < Integer.parseInt(a[1]); i++) {
			StringBuilder sb = new StringBuilder();
			for (int k = 2; k < a.length; k++) {
				sb.append(' ').append(a[k]).append('=').append(emu.readRegister(a[k]).toString(16));
			}
			println("step " + i + " pc=" + emu.getExecutionAddress() + " " + currentProgram.getListing().getInstructionAt(emu.getExecutionAddress()) + sb);
			if (!emu.step(monitor)) {
				println("stopped: " + emu.getLastError());
				break;
			}
		}
		emu.dispose();
	}
}
