// Imports a TMS320C54x boot-table image (e.g. the decrypted PSR-500/600 DSP firmware) as a
// new program in the current project. Each boot-table block becomes a program-space memory
// block; blocks in on-chip RAM (0x0080-0x7FFF, shared by program and data when OVLY=1) are
// mirrored into data space. The boot entry point is labelled reset_entry.
// Script Manager: asks for the file. Headless: script arguments <image> [<program name>].
// @category C54x
import ghidra.app.plugin.processors.generic.MemoryBlockDefinition;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.lang.AddressLabelInfo;
import ghidra.framework.model.DomainFolder;
import ghidra.program.database.ProgramDB;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.lang.CompilerSpec;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.LanguageID;
import ghidra.program.model.listing.Program;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.util.DefaultLanguageService;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.nio.file.Files;

public class C54xImportBootImage extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        File in = args.length > 0 ? new File(args[0]) : askFile("C54x boot-table image (decrypted)", "Import");
        String name = args.length > 1 ? args[1] : in.getName();
        byte[] raw = Files.readAllBytes(in.toPath());

        // words: skip an odd 2-byte prefix if the keyword isn't at the start
        int[] w = words(raw, 0);
        int k = find08aa(w);
        if (k < 0) { w = words(raw, 2); k = find08aa(w); }
        if (k < 0) throw new IllegalArgumentException("no 0x08AA boot-table keyword");
        int entry = w[k + 4];

        Language lang = DefaultLanguageService.getLanguageService()
                .getLanguage(new LanguageID("TMS320C54x:BE:16:default"));
        CompilerSpec cs = lang.getDefaultCompilerSpec();
        ProgramDB p = new ProgramDB(name, lang, cs, this);
        int tx = p.startTransaction("import boot table");
        try {
            Memory mem = p.getMemory();
            AddressSpace prog = p.getAddressFactory().getAddressSpace("prog");
            AddressSpace data = p.getAddressFactory().getAddressSpace("data");
            int i = k + 5, n = 0;
            while (i < w.length && w[i] != 0) {
                int size = w[i], xpc = w[i + 1], addr = w[i + 2];
                byte[] b = new byte[size * 2];
                for (int j = 0; j < size; j++) {
                    b[2 * j] = (byte) (w[i + 3 + j] >> 8);
                    b[2 * j + 1] = (byte) w[i + 3 + j];
                }
                Address a = prog.getTruncatedAddress(addr, true);   // word address
                MemoryBlock blk = mem.createInitializedBlock(String.format("prog_%04X", addr), a,
                        new ByteArrayInputStream(b), b.length, monitor, false);
                blk.setExecute(true);
                blk.setWrite(true);
                // on-chip DARAM is shared by program and data space (OVLY=1): mirror it
                if (addr >= 0x80 && addr + size <= 0x8000) {
                    try {
                        mem.createByteMappedBlock(String.format("data_%04X", addr), data.getTruncatedAddress(addr, true), a, b.length, false);
                    } catch (Exception e) {
                        println("no data-space mirror for 0x" + Integer.toHexString(addr) + ": " + e.getMessage());
                    }
                }
                println(String.format("block %d: prog 0x%04X-0x%04X (%d words, XPC %d)", n++, addr, addr + size - 1, size, xpc));
                i += 3 + size;
            }
            // what Ghidra's loaders do at import: processor memory blocks and register labels
            for (MemoryBlockDefinition def : lang.getDefaultMemoryBlocks()) {
                try {
                    def.createBlock(p);
                } catch (Exception e) {
                    println("skipped block " + def.getBlockName() + ": " + e.getMessage());
                }
            }
            for (AddressLabelInfo info : lang.getDefaultSymbols()) {
                p.getSymbolTable().createLabel(info.getAddress(), info.getLabel(), SourceType.IMPORTED);
            }
            Address ep = prog.getTruncatedAddress(entry, true);
            p.getSymbolTable().addExternalEntryPoint(ep);
            p.getSymbolTable().createLabel(ep, "reset_entry", SourceType.IMPORTED);
        } finally {
            p.endTransaction(tx, true);
        }
        DomainFolder root = state.getProject().getProjectData().getRootFolder();
        root.createFile(name, p, monitor);
        println("C54xImportBootImage: created " + name + ", entry 0x" + Integer.toHexString(entry));
        p.release(this);
    }

    static int[] words(byte[] b, int start) {
        int n = (b.length - start) / 2;
        int[] w = new int[n];
        for (int i = 0; i < n; i++) w[i] = ((b[start + 2 * i] & 0xff) << 8) | (b[start + 2 * i + 1] & 0xff);
        return w;
    }

    static int find08aa(int[] w) {
        for (int i = 0; i < Math.min(4, w.length); i++) if (w[i] == 0x08AA) return i;
        return -1;
    }
}
