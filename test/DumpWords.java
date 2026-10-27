// Decode the instruction at every 16-bit word address of the imported raw image (no analysis).
// Output per word: "<word-index> <length-in-words> <text>" (length 0 = no valid decode)
// Script args: <outfile> <slot-bytes> [pcode]   (addresses of word-addressed spaces count bytes here)
// The prototype cache is cleared after every word (CRC collisions, see DumpSlots in the other modules).
//@category Testing

import java.io.PrintStream;
import java.lang.reflect.Field;
import java.util.Map;

import ghidra.app.script.GhidraScript;
import ghidra.app.util.PseudoInstruction;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.InstructionPrototype;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.ProcessorContext;
import ghidra.program.model.lang.ProgramProcessorContext;
import ghidra.program.model.mem.MemBuffer;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.mem.MemoryBufferImpl;
import ghidra.program.model.pcode.PcodeOp;

public class DumpWords extends GhidraScript {
	@Override
	protected void run() throws Exception {
		String[] args = getScriptArgs();
		PrintStream out = new PrintStream(args[0]);
		long slot = Long.parseLong(args[1]);
		boolean pcode = args.length > 2 && args[2].equals("pcode");
		MemoryBlock block = currentProgram.getMemory().getBlocks()[0];
		Address base = block.getStart();
		long n = block.getSize();
		Language lang = currentProgram.getLanguage();
		Field fld = lang.getClass().getDeclaredField("instructProtoMap");
		fld.setAccessible(true);
		Map<?, ?> protoCache = (Map<?, ?>) fld.get(lang);
		for (long i = 0; i < n; i += slot) {
			Address a = base.add(i);
			String text;
			int len = 0;
			PseudoInstruction ins = null;
			try {
				ProcessorContext ctx = new ProgramProcessorContext(currentProgram.getProgramContext(), a);
				MemBuffer buf = new MemoryBufferImpl(currentProgram.getMemory(), a);
				InstructionPrototype p = lang.parse(buf, ctx, false);
				ins = new PseudoInstruction(currentProgram, a, p, buf, ctx);
				len = ins.getLength() / 2;
				text = ins.toString();
			}
			catch (Exception e) {
				text = "BAD";
			}
			out.printf("%d %d %s%n", i / slot, len, text);
			if (pcode && ins != null) {
				for (PcodeOp op : ins.getPcode()) {
					out.printf("    %s%n", op);
				}
			}
			protoCache.clear();
		}
		out.close();
	}
}
